from typing import List, Optional, Any
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel

from app.api.dependencies import get_db, get_current_user, require_tenant_id
from app.models.user import User, Role
from app.models.invoice import Invoice
from app.models.inventory_transaction import InventoryTransaction
from app.models.generated_report import GeneratedReport
from app.core import security
from app.schemas.user import UserResponse

router = APIRouter()


class StaffCreatePayload(BaseModel):
    full_name: str
    username: str
    password: str
    role_name: str = "Sales Staff"
    allowed_modules: List[str] = ["billing", "invoices", "exchange", "customers", "inventory"]


class StaffUpdatePayload(BaseModel):
    full_name: Optional[str] = None
    username: Optional[str] = None
    password: Optional[str] = None
    role_name: Optional[str] = None
    allowed_modules: Optional[List[str]] = None
    is_active: Optional[bool] = None


def _require_store_owner(current_user: User):
    if not current_user.is_owner:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the Shop Owner can manage staff accounts and permissions.",
        )


def _get_or_create_role(db: Session, role_name: str) -> Role:
    clean_role = (role_name or "Sales Staff").strip()
    if clean_role in ("Admin", "Shop Owner"):
        clean_role = "Store Manager"
    role = db.query(Role).filter(Role.name == clean_role).first()
    if not role:
        role = Role(name=clean_role, description=f"Store {clean_role}")
        db.add(role)
        db.commit()
        db.refresh(role)
    return role


def _sanitize_modules(modules: List[str]) -> List[str]:
    valid = [m.strip().lower() for m in modules if m and m.strip().lower() in User.ALL_MODULES]
    if not valid:
        valid = ["billing", "invoices"]
    return list(dict.fromkeys(valid))


@router.get("", response_model=List[UserResponse])
@router.get("/", response_model=List[UserResponse])
def list_staff_members(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    store_id = require_tenant_id(current_user)
    _require_store_owner(current_user)

    users = (
        db.query(User)
        .filter(User.tenant_id == store_id, User.id != current_user.id)
        .order_by(User.id.desc())
        .all()
    )
    # Return only non-owner staff members of this store
    return [u for u in users if not u.is_owner]


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def create_staff_member(
    payload: StaffCreatePayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    store_id = require_tenant_id(current_user)
    _require_store_owner(current_user)

    clean_username = payload.username.strip()
    clean_name = payload.full_name.strip()
    clean_password = payload.password

    if len(clean_username) < 3:
        raise HTTPException(status_code=400, detail="Username must be at least 3 characters long.")
    if len(clean_password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters long.")
    if not clean_name:
        raise HTTPException(status_code=400, detail="Staff full name is required.")

    existing = (
        db.query(User)
        .filter(
            (func.lower(User.username) == clean_username.lower())
            | (func.lower(User.email) == clean_username.lower())
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=400, detail="This username is already taken. Please choose another.")

    role = _get_or_create_role(db, payload.role_name)
    valid_modules = _sanitize_modules(payload.allowed_modules)

    new_staff = User(
        username=clean_username,
        full_name=clean_name,
        hashed_password=security.get_password_hash(clean_password),
        is_active=True,
        role_id=role.id,
        tenant_id=store_id,
        permissions=",".join(valid_modules),
        token_version=1,
    )
    db.add(new_staff)
    db.commit()
    db.refresh(new_staff)
    return new_staff


@router.put("/{staff_id}", response_model=UserResponse)
def update_staff_member(
    staff_id: int,
    payload: StaffUpdatePayload,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    store_id = require_tenant_id(current_user)
    _require_store_owner(current_user)

    staff = db.query(User).filter(User.id == staff_id, User.tenant_id == store_id).first()
    if not staff or staff.is_owner or staff.id == current_user.id:
        raise HTTPException(status_code=404, detail="Staff member not found.")

    if payload.full_name is not None and payload.full_name.strip():
        staff.full_name = payload.full_name.strip()

    if payload.username is not None and payload.username.strip():
        new_username = payload.username.strip()
        if len(new_username) < 3:
            raise HTTPException(status_code=400, detail="Username must be at least 3 characters long.")
        if new_username.lower() != staff.username.lower():
            dup = (
                db.query(User)
                .filter(
                    User.id != staff.id,
                    (func.lower(User.username) == new_username.lower())
                    | (func.lower(User.email) == new_username.lower()),
                )
                .first()
            )
            if dup:
                raise HTTPException(status_code=400, detail="This username is already taken.")
            staff.username = new_username

    session_bump = False

    if payload.password is not None and payload.password != "":
        if len(payload.password) < 6:
            raise HTTPException(status_code=400, detail="Password must be at least 6 characters long.")
        staff.hashed_password = security.get_password_hash(payload.password)
        session_bump = True

    if payload.role_name is not None:
        role = _get_or_create_role(db, payload.role_name)
        staff.role_id = role.id

    if payload.allowed_modules is not None:
        valid_modules = _sanitize_modules(payload.allowed_modules)
        staff.permissions = ",".join(valid_modules)

    if payload.is_active is not None:
        if staff.is_active != payload.is_active:
            staff.is_active = payload.is_active
            if not payload.is_active:
                session_bump = True

    if session_bump:
        staff.token_version = (getattr(staff, "token_version", 1) or 1) + 1

    db.commit()
    db.refresh(staff)
    return staff


@router.delete("/{staff_id}")
def delete_staff_member(
    staff_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Any:
    store_id = require_tenant_id(current_user)
    _require_store_owner(current_user)

    staff = db.query(User).filter(User.id == staff_id, User.tenant_id == store_id).first()
    if not staff or staff.is_owner or staff.id == current_user.id:
        raise HTTPException(status_code=404, detail="Staff member not found.")

    # Reassign historical records to store owner so foreign keys never fail
    db.query(Invoice).filter(Invoice.created_by == staff.id).update(
        {Invoice.created_by: current_user.id}, synchronize_session=False
    )
    db.query(InventoryTransaction).filter(InventoryTransaction.user_id == staff.id).update(
        {InventoryTransaction.user_id: current_user.id}, synchronize_session=False
    )
    db.query(GeneratedReport).filter(GeneratedReport.generated_by == staff.id).update(
        {GeneratedReport.generated_by: current_user.id}, synchronize_session=False
    )

    db.delete(staff)
    db.commit()
    return {"success": True, "message": "Staff member removed successfully."}
