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


from fastapi.responses import HTMLResponse
import urllib.request
import json

from app.models.store import Store

def _ensure_user_store(db: Session, user: User) -> User:
    if not user.tenant_id:
        existing_store = db.query(Store).filter(Store.owner_id == user.id).first()
        if existing_store:
            user.tenant_id = existing_store.id
            db.commit()
            db.refresh(user)
        else:
            name_seed = user.full_name or (user.email.split('@')[0] if user.email else user.username)
            store_name = f"{name_seed.title()} Jewellers"
            store = Store(
                name=store_name,
                owner_id=user.id,
                email=user.email,
                is_active=True
            )
            db.add(store)
            db.commit()
            db.refresh(store)
            user.tenant_id = store.id
            db.commit()
            db.refresh(user)
    return user

@router.get("/google-callback", response_class=HTMLResponse)
def google_callback() -> str:
    """OAuth callback bridge page for Mobile App Google Sign-In."""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Google Authentication</title>
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body style="background:#0a0a0a; color:#d4af37; font-family:sans-serif; text-align:center; padding-top:25%;">
        <h2>Authenticating with Saideep Jewellers...</h2>
        <p style="color:#aaa;">Please wait while we redirect back to the app.</p>
        <script>
            var hash = window.location.hash.substring(1);
            var query = window.location.search.substring(1);
            var params = new URLSearchParams(hash || query);
            var token = params.get('id_token') || params.get('access_token');
            if (token) {
                window.location.href = "jewellerapp://auth?token=" + encodeURIComponent(token);
            } else {
                document.body.innerHTML = "<h3 style='color:#ef4444;'>Authentication Failed.</h3><p>Could not extract Google Token.</p>";
            }
        </script>
    </body>
    </html>
    """

@router.post("/google-login", response_model=Token)
def google_login(
    payload: GoogleToken,
    db: Session = Depends(get_db)
) -> Any:
    email = None
    name = None
    token_str = payload.token.strip()

    # 1. Try verifying as Google ID token
    try:
        client_id = settings.GOOGLE_CLIENT_ID.strip() if settings.GOOGLE_CLIENT_ID else None
        idinfo = id_token.verify_oauth2_token(
            token_str, 
            google_requests.Request(), 
            client_id,
            clock_skew_in_seconds=10
        )
        email = idinfo.get("email")
        name = idinfo.get("name", email.split('@')[0] if email else "Google User")
    except Exception:
        # 2. Try fetching as Google Access token
        try:
            req = urllib.request.Request(
                "https://www.googleapis.com/oauth2/v3/userinfo", 
                headers={"Authorization": f"Bearer {token_str}"}
            )
            with urllib.request.urlopen(req, timeout=10) as resp:
                user_data = json.loads(resp.read().decode())
                email = user_data.get("email")
                name = user_data.get("name", email.split('@')[0] if email else "Google User")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid Google token or access token: {str(e)}")

    if not email:
        raise HTTPException(status_code=400, detail="Google authentication did not provide a valid email.")

    # Check if user exists
    user = user_repo.get_by_email(db, email=email)
    if not user:
        user = user_repo.get_by_username(db, username=email)
        
    if not user:
        admin_role = db.query(Role).filter(Role.name == "Admin").first()
        if not admin_role:
            admin_role = db.query(Role).first()
        role_id = admin_role.id if admin_role else 1
        
        pwd = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        hashed_password = security.get_password_hash(pwd)
        user = User(
            username=email,
            email=email,
            full_name=name or email.split('@')[0],
            hashed_password=hashed_password,
            is_active=True,
            role_id=role_id
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        
    _ensure_user_store(db, user)
    return _issue_token(user)

@router.get("/me", response_model=UserResponse)
def read_current_user(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)) -> Any:
    _ensure_user_store(db, current_user)
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
    
    _ensure_user_store(db, db_obj)
    return db_obj


class ForgotPasswordRequest(BaseModel):
    email: str


class ResetPasswordRequest(BaseModel):
    email: str
    new_password: str


@router.post("/forgot-password")
def forgot_password(req: ForgotPasswordRequest, db: Session = Depends(get_db)):
    email_clean = req.email.strip()
    user = user_repo.get_by_email(db, email=email_clean)
    if not user:
        user = user_repo.get_by_username(db, username=email_clean)
    if not user:
        raise HTTPException(status_code=404, detail="No registered account found with this email address.")
    
    return {
        "success": True,
        "message": f"Password reset verified for {email_clean}."
    }


@router.post("/reset-password")
def reset_password(req: ResetPasswordRequest, db: Session = Depends(get_db)):
    email_clean = req.email.strip()
    if len(req.new_password.strip()) < 4:
        raise HTTPException(status_code=400, detail="Password must be at least 4 characters long.")
        
    user = user_repo.get_by_email(db, email=email_clean)
    if not user:
        user = user_repo.get_by_username(db, username=email_clean)
    if not user:
        raise HTTPException(status_code=404, detail="No registered account found with this email address.")
        
    user.hashed_password = security.get_password_hash(req.new_password.strip())
    db.commit()
    db.refresh(user)
    return {
        "success": True,
        "message": "Password updated successfully! You can now log in with your new password."
    }

