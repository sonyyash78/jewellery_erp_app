"""Initialize admin role and user.
Call this after the app is fully initialized to avoid circular imports.
"""
from app.db.database import SessionLocal
from app.models.user import User, Role
from app.core.security import get_password_hash, verify_password


def init_admin():
    """Create Admin role and admin user if they don't exist.
    
    This function is idempotent - running it multiple times won't create duplicates.
    """
    db = SessionLocal()
    try:
        # Check if Admin role exists
        admin_role = db.query(Role).filter(Role.name == "Admin").first()
        if not admin_role:
            admin_role = Role(name="Admin", description="Super Administrator")
            db.add(admin_role)
            db.commit()
            db.refresh(admin_role)
            print("Created Admin Role")

        # Check if admin user exists
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            # Create new admin user
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
            # If password doesn't match, update it
            if not verify_password("admin123", admin_user.hashed_password):
                admin_user.hashed_password = get_password_hash("admin123")
                db.commit()
                print("Reset admin password to admin123")
            else:
                print("Admin user already exists with correct password")
    finally:
        db.close()


if __name__ == "__main__":
    init_admin()
