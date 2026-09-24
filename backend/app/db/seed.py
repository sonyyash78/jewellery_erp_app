"""Seed default Admin role and admin user.
Run this directly: python -m app.db.seed
"""
import sys
import os

# Add backend directory to path
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# Import what we need directly - avoiding circular imports
from app.db.database import SessionLocal
from app.models.user import User, Role
from app.core.security import get_password_hash, verify_password


def seed_db():
    """Create Admin role and admin user if they don't exist.
    
    This function is idempotent - running it multiple times won't create duplicates.
    """
    db = SessionLocal()
    try:
        admin_role = db.query(Role).filter(Role.name == "Admin").first()
        if not admin_role:
            admin_role = Role(name="Admin", description="Super Administrator")
            db.add(admin_role)
            db.commit()
            db.refresh(admin_role)
            print("Created Admin Role")

        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            admin_user = User(
                username="admin",
                email="admin@jewelleryerp.com",
                full_name="Super Admin",
                hashed_password=get_password_hash("admin123"),
                role_id=admin_role.id,
                is_active=True,
            )
            db.add(admin_user)
            db.commit()
            print("Created Default Admin User (admin / admin123)")
        else:
            if not verify_password("admin123", admin_user.hashed_password):
                admin_user.hashed_password = get_password_hash("admin123")
                db.commit()
                print("Reset admin password to admin123")
            else:
                print("Admin user already exists")
    finally:
        db.close()


if __name__ == "__main__":
    seed_db()
