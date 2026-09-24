from app.db.database import SessionLocal
from app.models.user import User, Role
from app.core.security import get_password_hash

db = SessionLocal()

# Create Admin role if it doesn't exist
role = db.query(Role).filter(Role.name == "Admin").first()
if not role:
    role = Role(
        name="Admin",
        description="Administrator"
    )
    db.add(role)
    db.commit()
    db.refresh(role)

# Create admin user if it doesn't exist
user = db.query(User).filter(User.username == "admin").first()
if not user:
    user = User(
        username="admin",
        email="admin@example.com",
        full_name="System Admin",
        hashed_password=get_password_hash("admin123"),
        role_id=role.id,
        is_active=True
    )
    db.add(user)
    db.commit()
    print("Admin user created.")
else:
    print("Admin already exists.")

db.close()