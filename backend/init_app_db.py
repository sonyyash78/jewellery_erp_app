"""
Initialize standalone database for Mobile App (jeweller_app_db)
Creates all tables and seeds essential data (admin user, metal rates, store settings).
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(__file__))

from datetime import datetime, date
from app.db.database import engine, SessionLocal, Base
from app.models.user import User, Role
from app.models.setting import Setting
from app.models.metal_rates import MetalRate
from app.core.security import get_password_hash

def init_database():
    print("Creating all tables in jeweller_app_db...")
    Base.metadata.create_all(bind=engine)
    print("Tables created successfully!")

    db = SessionLocal()
    try:
        # 1. Admin Role & User
        admin_role = db.query(Role).filter(Role.name == "Admin").first()
        if not admin_role:
            admin_role = Role(name="Admin", description="Administrator with full access")
            db.add(admin_role)
            db.commit()
            db.refresh(admin_role)

        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin = User(
                username="admin",
                email="admin@saideep.com",
                hashed_password=get_password_hash("admin123"),
                full_name="System Administrator",
                role_id=admin_role.id,
                is_active=True
            )
            db.add(admin)
            print("Admin user created: admin / admin123")

        # 2. Store Settings
        default_settings = [
            ("business_name", "SAIDEEP JEWELLERS"),
            ("tagline", "TIMELESS BEAUTY. TRUSTED FOREVER."),
            ("phone", "9460820878"),
            ("email", "saideepjewellers74@gmail.com"),
            ("address", "Takhatgarh khedawas"),
            ("gstin", "BNUPK1610E1Z3"),
            ("pan", "BNUPK1610E"),
            ("upi_id", "yashsoni123478-1@okhdfcbank"),
            ("upi_name", "SAIDEEP JEWELLERS"),
            ("bank_name", "HDFC Bank"),
            ("bank_account_no", ""),
            ("bank_ifsc", ""),
            ("print_hallmark", "BIS 916 (Gold)\nBIS 925 (Silver)"),
            ("print_wastage", "0.00%"),
            ("print_making_charges", "Gold ₹ 1,000.00/gm\nSilver ₹ 20.00/gm"),
            ("print_remarks", "Thank you for shopping with us!"),
            ("qr_amount_type", "exact"),
        ]
        for key, val in default_settings:
            existing = db.query(Setting).filter(Setting.key == key).first()
            if not existing:
                db.add(Setting(key=key, value=val))
        print("Default store settings configured!")

        # 3. Default Metal Rates
        today = date.today()
        existing_rate = db.query(MetalRate).first()
        if not existing_rate:
            db.add(MetalRate(metal_type="Gold", purity="24K", rate_per_gram=7250.0, date=today))
            print("Default metal rates configured!")

        db.commit()
        print("App Database initialized completely and independently!")
    except Exception as e:
        db.rollback()
        print("Error during seeding:", e)
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
