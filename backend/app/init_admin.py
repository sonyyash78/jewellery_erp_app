"""Initialize admin role, store, rates, and default offline user.
Call this after the app is fully initialized to avoid circular imports.
"""
import os
import secrets
from decimal import Decimal
from datetime import datetime
from app.db.database import SessionLocal
from app.models.user import User, Role
from app.models.store import Store
from app.models.gold_rate import GoldRate
from app.models.silver_rate import SilverRate
from app.models.purity import Purity
from app.models.metal_type import MetalType
from app.services.metal_rate_service import seed_default_metals
from app.core.security import get_password_hash
from app.core.config import settings


def init_admin():
    """Create Admin role, store, rates, and default admin user if they don't exist.
    
    This function is strictly idempotent - running it multiple times preserves existing data.
    """
    db = SessionLocal()
    try:
        # 1. Seed Core Roles
        roles_data = [
            ("Admin", "Super Administrator"),
            ("Shop Owner", "Jewellery Store Owner"),
            ("Staff", "Store Sales & Inventory Staff"),
        ]
        admin_role = None
        for role_name, role_desc in roles_data:
            role = db.query(Role).filter(Role.name == role_name).first()
            if not role:
                role = Role(name=role_name, description=role_desc)
                db.add(role)
                db.commit()
                db.refresh(role)
            if role_name == "Admin":
                admin_role = role

        # 2. Seed Default Store if not exists
        default_store = db.query(Store).filter(Store.id == 1).first()
        if not default_store:
            default_store = Store(
                id=1,
                name="Saideep Jewellers",
                tagline="Purity & Trust Since Inception",
                phone="9876543210",
                email="info@saideepjewellers.com",
                city="Mumbai",
                state="Maharashtra",
                pincode="400001",
                is_active=True
            )
            db.add(default_store)
            db.commit()
            db.refresh(default_store)
            print("[BOOTSTRAP] Created default store: Saideep Jewellers")

        # 3. Seed Default Metals and Purities
        seed_default_metals(db)

        # 4. Seed Default Metal Rates if not exists
        purity_24k = db.query(Purity).join(MetalType).filter(MetalType.name == "Gold", Purity.karat_name == "24K").first()
        if purity_24k and not db.query(GoldRate).filter(GoldRate.purity_id == purity_24k.id).first():
            db.add(GoldRate(
                purity_id=purity_24k.id,
                rate_per_gram=Decimal("7500.00"),
                effective_datetime=datetime.now()
            ))
            print("[BOOTSTRAP] Initialized default 24K Gold Rate: Rs. 7,500/g")

        purity_22k = db.query(Purity).join(MetalType).filter(MetalType.name == "Gold", Purity.karat_name == "22K").first()
        if purity_22k and not db.query(GoldRate).filter(GoldRate.purity_id == purity_22k.id).first():
            db.add(GoldRate(
                purity_id=purity_22k.id,
                rate_per_gram=Decimal("6875.00"),
                effective_datetime=datetime.now()
            ))
            print("[BOOTSTRAP] Initialized default 22K Gold Rate: Rs. 6,875/g")

        purity_999 = db.query(Purity).join(MetalType).filter(MetalType.name == "Silver", Purity.karat_name == "999").first()
        if purity_999 and not db.query(SilverRate).filter(SilverRate.purity_id == purity_999.id).first():
            db.add(SilverRate(
                purity_id=purity_999.id,
                rate_per_gram=Decimal("90.00"),
                effective_datetime=datetime.now()
            ))
            print("[BOOTSTRAP] Initialized default 999 Silver Rate: Rs. 90/g")
        db.commit()

        # 5. Seed Default Admin User if not exists
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            initial_password = os.getenv("INITIAL_ADMIN_PASSWORD")
            is_offline = (
                os.getenv("OFFLINE_MODE", "false").lower() in ("true", "1") or
                getattr(settings, "DATABASE_URL", "").startswith("sqlite")
            )
            if not initial_password:
                if is_offline:
                    initial_password = "admin"
                    print("[BOOTSTRAP] Offline mode active. Default admin password set to 'admin'")
                else:
                    initial_password = secrets.token_urlsafe(16)
                    if os.getenv("ENVIRONMENT", "development").lower() != "production":
                        print(f"[BOOTSTRAP] Generated bootstrap admin password: {initial_password}")
                    else:
                        print("[BOOTSTRAP] Generated random bootstrap admin password. To set a known password, supply INITIAL_ADMIN_PASSWORD.")

            admin_user = User(
                username="admin",
                email="admin@jewelleryerp.com",
                full_name="Administrator",
                hashed_password=get_password_hash(initial_password),
                role_id=admin_role.id if admin_role else 1,
                tenant_id=1,
                is_active=True,
                token_version=1
            )
            db.add(admin_user)
            db.commit()
            print("[BOOTSTRAP] Created initial administrator account (username: admin).")
        else:
            print("Admin user already exists. Preserving credentials.")
    except Exception as e:
        print(f"[BOOTSTRAP WARNING] init_admin encountered an issue: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    init_admin()
