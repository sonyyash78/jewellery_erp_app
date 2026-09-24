from typing import Generator
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import SessionLocal, engine  # noqa: F401 — re-exported for app.main
from app.models.user import User
from app.schemas.auth import TokenPayload

def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

security = HTTPBearer()

def get_current_user(
    db: Session = Depends(get_db), token: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    try:
        payload = jwt.decode(
            token.credentials, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        token_data = TokenPayload(**payload)

        if token_data.type and token_data.type != "access":
            raise HTTPException(status_code=403, detail="Not an access token")

    except (jwt.PyJWTError, ValidationError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not token_data.sub:
        raise HTTPException(status_code=401, detail="Could not validate credentials")

    # Prefer numeric user id; fall back to username for older tokens
    user = None
    if str(token_data.sub).isdigit():
        user = db.query(User).filter(User.id == int(token_data.sub)).first()
    if not user:
        user = db.query(User).filter(User.username == str(token_data.sub)).first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user

class RoleChecker:
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: User = Depends(get_current_user)):
        role_name = None
        if getattr(user, "role", None) is not None:
            role_name = user.role.name
        elif getattr(user, "roles", None):
            role_names = [r.name for r in user.roles]
            if any(r in self.allowed_roles for r in role_names):
                return user
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation not permitted for this role",
            )

        if role_name and role_name in self.allowed_roles:
            return user

        # Allow if no role assigned yet (dev bootstrap)
        if role_name is None and "Admin" in self.allowed_roles:
            return user

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Operation not permitted for this role",
        )
