from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.db.database import Base

class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(String(255))
    users = relationship("User", back_populates="role")

class Permission(Base):
    __tablename__ = "permissions"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(100))
    is_active = Column(Boolean, default=True)
    role_id = Column(Integer, ForeignKey("roles.id"))
    tenant_id = Column(Integer, ForeignKey("stores.id", ondelete="SET NULL"), nullable=True)
    token_version = Column(Integer, default=1, nullable=False, server_default="1")
    permissions = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    role = relationship("Role", back_populates="users")
    store = relationship("Store", back_populates="users", foreign_keys=[tenant_id])
    invoices = relationship("Invoice", back_populates="creator")
    inventory_transactions = relationship("InventoryTransaction", back_populates="user")
    reports = relationship("GeneratedReport", back_populates="generator")

    ALL_MODULES = [
        "dashboard",
        "customers",
        "inventory",
        "billing",
        "invoices",
        "exchange",
        "purchases",
        "reports",
        "settings",
    ]

    ROLE_DEFAULT_MODULES = {
        "Admin": ALL_MODULES,
        "Shop Owner": ALL_MODULES,
        "Store Manager": ["dashboard", "customers", "inventory", "billing", "invoices", "exchange", "purchases", "reports"],
        "Sales Staff": ["billing", "invoices", "exchange", "customers", "inventory"],
        "Inventory Staff": ["inventory", "purchases"],
    }

    @property
    def store_name(self) -> str:
        return self.store.name if self.store else "Jewellery ERP"

    @property
    def logo_url(self) -> str:
        if self.store and self.store.logo_url:
            return self.store.logo_url
        return f"/static/logo_store_{self.tenant_id or 1}.png"

    @property
    def role_name(self) -> str:
        if self.role and self.role.name:
            return self.role.name
        return "Shop Owner"

    @property
    def is_owner(self) -> bool:
        if self.id == 1:
            return True
        if self.store and self.store.owner_id == self.id:
            return True
        if self.role and self.role.name in ("Admin", "Shop Owner"):
            return True
        if not self.role and not self.permissions:
            return True
        return False

    @property
    def allowed_modules(self) -> list[str]:
        if self.is_owner:
            return list(self.ALL_MODULES)
        if self.permissions is not None and self.permissions.strip() != "":
            return [m.strip() for m in self.permissions.split(",") if m.strip()]
        return list(self.ROLE_DEFAULT_MODULES.get(self.role_name, ["billing", "invoices", "exchange", "customers", "inventory"]))

