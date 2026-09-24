from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.api.dependencies import get_current_user
from app.core import security
from app.core.config import settings
from app.repositories.user_repo import user_repo
from app.schemas.user import Token, UserResponse, UserCreate
from app.models.user import User, Role
from pydantic import BaseModel
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
import string
import random

router = APIRouter()

class GoogleToken(BaseModel):
    token: str


def _issue_token(user: User) -> dict:
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }


def _authenticate(db: Session, username_or_email: str, password: str) -> User:
    # Try username first
    user = user_repo.get_by_username(db, username=username_or_email)
    # If not found, try email
    if not user:
        user = user_repo.get_by_email(db, email=username_or_email)
        
    if not user or not security.verify_password(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username, email, or password")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user


@router.post("/login", response_model=Token)
async def login(request: Request, db: Session = Depends(get_db)) -> Any:
    """Accept JSON {username, password} or OAuth2 form-urlencoded."""
    content_type = (request.headers.get("content-type") or "").lower()
    username = password = None

    if "application/json" in content_type:
        body = await request.json()
        username = body.get("username")
        password = body.get("password")
    else:
        form = await request.form()
        username = form.get("username")
        password = form.get("password")

    if not username or not password:
        raise HTTPException(status_code=422, detail="username and password required")

    user = _authenticate(db, str(username), str(password))
    return _issue_token(user)


@router.post("/token", response_model=Token)
def login_oauth2_form(
    db: Session = Depends(get_db), form_data: OAuth2PasswordRequestForm = Depends()
) -> Any:
    """OAuth2 password flow for Swagger Authorize."""
    user = _authenticate(db, form_data.username, form_data.password)
    return _issue_token(user)


@router.post("/google-login", response_model=Token)
def google_login(
    payload: GoogleToken,
    db: Session = Depends(get_db)
) -> Any:
    try:
        # Verify token
        idinfo = id_token.verify_oauth2_token(
            payload.token, 
            google_requests.Request(), 
            settings.GOOGLE_CLIENT_ID,
            clock_skew_in_seconds=10
        )
        
        email = idinfo.get("email")
        if not email:
            raise HTTPException(status_code=400, detail="Google token does not contain email")
            
        # Check if user exists
        user = user_repo.get_by_email(db, email=email)
        
        if not user:
            # Check by username just in case
            user = user_repo.get_by_username(db, username=email)
            
        if not user:
            # Create user
            pwd = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
            hashed_password = security.get_password_hash(pwd)
            user = User(
                username=email,
                email=email,
                full_name=idinfo.get("name", email.split('@')[0]),
                hashed_password=hashed_password,
                is_active=True,
                role_id=1
            )
            # if role_id is required, we should fetch a default one or just leave None if nullable
            db.add(user)
            db.commit()
            db.refresh(user)
            
        return _issue_token(user)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid Google token: {str(e)}")

@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_user)) -> Any:
    return current_user


@router.post("/register", response_model=UserResponse)
def register_user(
    *,
    db: Session = Depends(get_db),
    user_in: UserCreate
) -> Any:
    """Register new user."""
    user = user_repo.get_by_username(db, username=user_in.username)
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    
    if user_in.email:
        user_email = user_repo.get_by_email(db, email=user_in.email)
        if user_email:
            raise HTTPException(
                status_code=400,
                detail="A user with this email address already exists.",
            )

    # Validate role_id exists
    if user_in.role_id is not None:
        role = db.query(Role).filter(Role.id == user_in.role_id).first()
        if not role:
            raise HTTPException(
                status_code=400,
                detail=f"Role with id {user_in.role_id} does not exist.",
            )

    hashed_password = security.get_password_hash(user_in.password)
    db_obj = User(
        username=user_in.username,
        email=user_in.email,
        full_name=user_in.full_name,
        hashed_password=hashed_password,
        role_id=user_in.role_id,
        is_active=True
    )
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj
