import sys
sys.path.append(r"C:\Users\YASH SONI\Desktop\jeweller-app\backend")

from app.db.database import SessionLocal
from app.models.stock_item import StockItem
from app.models.user import User

db = SessionLocal()

print("=== CHECKING STOCK ITEMS IN DB ===")
items = db.query(StockItem).all()
for itm in items:
    print(f"ID: {itm.id}, Code: {itm.item_code}, Name: {itm.item_name}, Metal: {itm.metal}, Weight: {itm.net_weight}g, Company ID: {itm.company_id}")

# Count items per company
c1_items = db.query(StockItem).filter(StockItem.company_id == 1).all()
c2_items = db.query(StockItem).filter(StockItem.company_id == 2).all()

print(f"\nCompany 1 (Without GST) items count: {len(c1_items)}")
for itm in c1_items:
    print(f"  [Co 1] {itm.item_code} - {itm.item_name} ({itm.net_weight}g)")

print(f"\nCompany 2 (GST) items count: {len(c2_items)}")
for itm in c2_items:
    print(f"  [Co 2] {itm.item_code} - {itm.item_name} ({itm.net_weight}g)")

db.close()
