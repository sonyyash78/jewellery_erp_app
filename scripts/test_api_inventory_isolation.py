import sys
sys.path.append(r"C:\Users\YASH SONI\Desktop\jeweller-app\backend")

from fastapi.testclient import TestClient
from app.main import app
from app.core.security import create_access_token

client = TestClient(app)

# Generate admin auth token
token = create_access_token(subject="admin")
headers = {"Authorization": f"Bearer {token}"}

print("=== 1. Querying Company 1 inventory ===")
res1 = client.get("/api/v1/stock/?company_id=1", headers=headers)
print("Status:", res1.status_code, "Total:", res1.json().get("total"), "Items:", [i["item_code"] for i in res1.json().get("items", [])])

print("\n=== 2. Querying Company 2 inventory ===")
res2 = client.get("/api/v1/stock/?company_id=2", headers=headers)
print("Status:", res2.status_code, "Total:", res2.json().get("total"), "Items:", [i["item_code"] for i in res2.json().get("items", [])])

print("\n=== 3. Scan GLD-000001 under Company 1 ===")
scan1 = client.get("/api/v1/stock/scan/GLD-000001?company_id=1", headers=headers)
print("Status:", scan1.status_code, "Item Name:", scan1.json().get("item_name"))

print("\n=== 4. Scan GLD-000001 under Company 2 (Should reject with 400) ===")
scan2 = client.get("/api/v1/stock/scan/GLD-000001?company_id=2", headers=headers)
print("Status:", scan2.status_code, "Detail:", scan2.json().get("detail"))
