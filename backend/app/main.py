from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from app.db.base_class import Base
from app.api.dependencies import engine

# Import model packages so metadata is populated (avoid duplicate class conflicts)
from app.models import *  # noqa: F401,F403 — Stack A CRM/billing
from app.models.exchange import Exchange  # noqa: F401
from app.models.exchange_item import ExchangeItem  # noqa: F401
from app.models.exchange_new_item import ExchangeNewItem  # noqa: F401
from app.models.invoice import Invoice  # noqa: F401
from app.models.invoice_item import InvoiceItem  # noqa: F401
from app.models.gold_calculation import GoldCalculation  # noqa: F401
from app.models.silver_calculation import SilverCalculation  # noqa: F401
from app.models.stock_item import StockItem  # noqa: F401
from app.models.seller import Seller  # noqa: F401
from app.models.purchase import Purchase  # noqa: F401
from app.models.purchase_item import PurchaseItem  # noqa: F401
from app.models.customer_ledger import CustomerLedger  # noqa: F401
from app.models.supplier_ledger import SupplierLedger  # noqa: F401
from app.models.metal_type import MetalType  # noqa: F401
from app.models.purity import Purity  # noqa: F401
from app.models.gold_rate import GoldRate  # noqa: F401
from app.models.silver_rate import SilverRate  # noqa: F401
from app.models.product import Product  # noqa: F401
from app.models.design import Design  # noqa: F401
from app.models.stone import Stone  # noqa: F401
from app.models.product_variant import ProductVariant  # noqa: F401
from app.models.product_image import ProductImage  # noqa: F401
from app.models.product_variant_stone import ProductVariantStone  # noqa: F401
from app.models.inventory_item import InventoryItem  # noqa: F401
from app.models.inventory_transaction import InventoryTransaction  # noqa: F401
from app.models.warehouse import Warehouse  # noqa: F401
from app.models.setting import Setting  # noqa: F401

from app.api.v1.auth import router as auth_router
from app.api.v1.customers import router as customers_router
from app.api.v1.suppliers import router as suppliers_router
from app.api.v1.inventory import router as inventory_router
from app.api.v1.metal_rates import router as metal_rates_router
from app.api.v1.products import router as products_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.invoices import router as invoices_router
from app.api.v1.sales import router as sales_router
from app.api.v1.sellers import router as sellers_router
from app.api.v1.purchases import router as purchases_router
from app.api.v1.stock import router as stock_router
from app.api.v1.exchanges import router as exchanges_router
from app.api.v1.reports import router as reports_router
from app.api.v1.settings import router as settings_router
from app.api.v1.billing import router as billing_router
from app.api.v1.ai import router as ai_router
from app.api.v1.backup import router as backup_router

# Migrate legacy Stack-A exchanges table if schema does not match Stack-B model
from sqlalchemy import inspect, text

def _ensure_schema():
    insp = inspect(engine)
    tables = insp.get_table_names()
    
    # 1. Migrate exchanges table if total_old_value missing
    if "exchanges" in tables:
        cols = {c["name"] for c in insp.get_columns("exchanges")}
        if "total_old_value" not in cols:
            with engine.begin() as conn:
                conn.execute(text("DROP TABLE IF EXISTS exchange_new_items"))
                conn.execute(text("DROP TABLE IF EXISTS exchange_items"))
                conn.execute(text("DROP TABLE IF EXISTS exchanges"))
    
    # 2. Check if exchange_new_items.stock_item_id is nullable, if not, drop it to recreate
    if "exchange_new_items" in tables:
        cols = {c["name"]: c for c in insp.get_columns("exchange_new_items")}
        if "stock_item_id" in cols and not cols["stock_item_id"].get("nullable", False):
            with engine.begin() as conn:
                conn.execute(text("DROP TABLE IF EXISTS exchange_new_items"))
                
    Base.metadata.create_all(bind=engine)

_ensure_schema()

from app.core.config import settings
from fastapi import Request

app = FastAPI(
    title="Jewellery ERP API",
    description="Backend API for Jewellery ERP System",
    version="1.0.0"
)

@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response

origins = [origin.strip() for origin in settings.CORS_ORIGINS.split(",")]
allow_origins = ["*"] if origins == ["*"] else origins
allow_credentials = True if origins != ["*"] else False

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(customers_router, prefix="/api/v1/customers", tags=["Customers"])
app.include_router(suppliers_router, prefix="/api/v1/suppliers", tags=["Suppliers"])
app.include_router(inventory_router, prefix="/api/v1/inventory", tags=["Inventory"])
app.include_router(metal_rates_router, prefix="/api/v1/metal-rates", tags=["Metal Rates"])
app.include_router(products_router, prefix="/api/v1/products", tags=["Products"])
app.include_router(dashboard_router, prefix="/api/v1/dashboard", tags=["Dashboard"])
app.include_router(invoices_router, prefix="/api/v1/invoices", tags=["Invoices"])
app.include_router(sales_router, prefix="/api/v1/sales", tags=["Sales"])
app.include_router(sellers_router, prefix="/api/v1/sellers", tags=["Sellers"])
app.include_router(purchases_router, prefix="/api/v1/purchases", tags=["Purchases"])
app.include_router(stock_router, prefix="/api/v1/stock", tags=["Stock"])
app.include_router(exchanges_router, prefix="/api/v1/exchanges", tags=["Exchanges"])
app.include_router(reports_router, prefix="/api/v1/reports", tags=["Reports"])
app.include_router(settings_router, prefix="/api/v1/settings", tags=["Settings"])
app.include_router(billing_router, prefix="/api/v1/billing", tags=["Billing"])
app.include_router(ai_router, prefix="/api/v1/ai", tags=["AI"])
app.include_router(backup_router, prefix="/api/v1/backup", tags=["Backup"])

static_dir = os.path.join(os.path.dirname(__file__), "..", "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

@app.get("/")
def root():
    return {"message": "Welcome to Jewellery ERP API. Visit /docs for the Swagger UI."}
