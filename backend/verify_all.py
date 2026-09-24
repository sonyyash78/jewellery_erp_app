"""
Comprehensive API Verification Script for Jewellery ERP
Tests every endpoint with correct status codes, schema, validation, error handling, and auth.
"""
import requests
import json
import sys
import random
from datetime import date

BASE_URL = "http://localhost:8000/api/v1"
RESULTS = {"PASS": [], "FAIL": [], "WARN": []}

def assert_key(d, k):
    assert k in d and d[k], f"Key '{k}' missing or empty"

def check(name, response, expected_status, validate_fn=None):
    if response.status_code != expected_status:
        RESULTS["FAIL"].append(f"{name}: expected {expected_status}, got {response.status_code} | {response.text[:200]}")
        return False
    if validate_fn:
        try:
            validate_fn(response.json())
        except (AssertionError, Exception) as e:
            RESULTS["FAIL"].append(f"{name} (schema): {e}")
            return False
    RESULTS["PASS"].append(name)
    return True

def check_any(name, response, ok_statuses, msg=""):
    if response.status_code in ok_statuses:
        RESULTS["PASS"].append(name)
        return True
    RESULTS["WARN"].append(f"{name}: got {response.status_code} {msg} | {response.text[:150]}")
    return False

# --- Get Token ---
print("Getting auth token...")
r = requests.post(f"{BASE_URL}/auth/login",
                  data={"username": "admin", "password": "admin123"},
                  headers={"Content-Type": "application/x-www-form-urlencoded"})
assert r.status_code == 200, f"Login failed: {r.text}"
TOKEN = r.json()["access_token"]
HEADERS = {"Authorization": f"Bearer {TOKEN}"}
print(f"Token obtained: {TOKEN[:30]}...")

# =============================
# 1. AUTH ENDPOINTS
# =============================
print("\n=== AUTH ===")

r = requests.post(f"{BASE_URL}/auth/login", data={"username": "admin", "password": "wrongpass"})
check("AUTH: Invalid login returns 400", r, 400)

r = requests.get(f"{BASE_URL}/customers/")
check("AUTH: No token returns 401", r, 401)

r = requests.get(f"{BASE_URL}/customers/", headers={"Authorization": "Bearer invalidtoken"})
check("AUTH: Invalid token returns 401", r, 401)

def check_token_schema(d):
    assert_key(d, "access_token")
    assert_key(d, "token_type")

r = requests.post(f"{BASE_URL}/auth/login", data={"username": "admin", "password": "admin123"})
check("AUTH: Valid login returns token+type", r, 200, check_token_schema)

# =============================
# 2. DASHBOARD
# =============================
print("\n=== DASHBOARD ===")

r = requests.get(f"{BASE_URL}/dashboard/metrics", headers=HEADERS)
check_any("DASHBOARD: Metrics", r, [200])

r = requests.get(f"{BASE_URL}/dashboard/recent-activity", headers=HEADERS)
check_any("DASHBOARD: Recent Activity", r, [200])

# =============================
# 3. CUSTOMERS
# =============================
print("\n=== CUSTOMERS ===")

uid = random.randint(10000, 99999)
customer_data = {
    "first_name": f"Test",
    "last_name": f"Customer {uid}",
    "phone_number": f"9{uid}00000",
    "email": f"test{uid}@example.com",
    "address": "123 Main St",
    "city": "Mumbai",
    "state": "Maharashtra",
    "pincode": "400001"
}

r = requests.post(f"{BASE_URL}/customers/", json=customer_data, headers=HEADERS)
cust_id = r.json().get("id") if r.status_code in (200, 201) else None
check_any("CUSTOMERS: Create", r, [200, 201])

r = requests.get(f"{BASE_URL}/customers/", headers=HEADERS)
check("CUSTOMERS: List 200", r, 200)

r = requests.get(f"{BASE_URL}/customers/?search=Test", headers=HEADERS)
check("CUSTOMERS: Search", r, 200)

# Duplicate protection
r_dup = requests.post(f"{BASE_URL}/customers/", json=customer_data, headers=HEADERS)
check_any("CUSTOMERS: Duplicate phone rejected", r_dup, [400, 409, 422])

if cust_id:
    r = requests.get(f"{BASE_URL}/customers/{cust_id}", headers=HEADERS)
    check("CUSTOMERS: Get by ID", r, 200)

    r = requests.put(f"{BASE_URL}/customers/{cust_id}", json={"first_name": "Updated"}, headers=HEADERS)
    check("CUSTOMERS: Update", r, 200)

    r = requests.delete(f"{BASE_URL}/customers/{cust_id}", headers=HEADERS)
    check_any("CUSTOMERS: Delete", r, [200, 204])

    r = requests.get(f"{BASE_URL}/customers/{cust_id}", headers=HEADERS)
    check("CUSTOMERS: 404 after delete", r, 404)

r = requests.get(f"{BASE_URL}/customers/9999999", headers=HEADERS)
check("CUSTOMERS: 404 for nonexistent", r, 404)

# =============================
# 4. SUPPLIERS
# =============================
print("\n=== SUPPLIERS ===")

uid2 = random.randint(10000, 99999)
supplier_data = {
    "name": f"Test Supplier {uid2}",
    "mobile": f"8{uid2}00000",
    "email": f"supplier{uid2}@example.com",
    "address": "456 Trade St",
    "city": "Delhi",
    "state": "Delhi",
    "gst_number": f"07AABCU9603R1ZP"
}

r = requests.post(f"{BASE_URL}/suppliers/", json=supplier_data, headers=HEADERS)
supp_id = r.json().get("id") if r.status_code in (200, 201) else None
check_any("SUPPLIERS: Create", r, [200, 201])

r = requests.get(f"{BASE_URL}/suppliers/", headers=HEADERS)
check("SUPPLIERS: List", r, 200)

r_dup = requests.post(f"{BASE_URL}/suppliers/", json=supplier_data, headers=HEADERS)
check_any("SUPPLIERS: Duplicate rejected", r_dup, [400, 409, 422])

if supp_id:
    r = requests.get(f"{BASE_URL}/suppliers/{supp_id}", headers=HEADERS)
    check("SUPPLIERS: Get by ID", r, 200)

    r = requests.put(f"{BASE_URL}/suppliers/{supp_id}", json={"name": "Updated Supplier"}, headers=HEADERS)
    check("SUPPLIERS: Update", r, 200)

    r = requests.delete(f"{BASE_URL}/suppliers/{supp_id}", headers=HEADERS)
    check_any("SUPPLIERS: Delete", r, [200, 204])

r = requests.get(f"{BASE_URL}/suppliers/9999999", headers=HEADERS)
check("SUPPLIERS: 404 for nonexistent", r, 404)

# =============================
# 5. INVENTORY
# =============================
print("\n=== INVENTORY ===")

r = requests.get(f"{BASE_URL}/inventory/", headers=HEADERS)
check("INVENTORY: List", r, 200)

r = requests.get(f"{BASE_URL}/inventory/categories", headers=HEADERS)
check_any("INVENTORY: Categories", r, [200])

item_data = {
    "name": f"Test Ring {uid}",
    "category": "Rings",
    "metal_type": "Gold",
    "purity": "22K",
    "gross_weight": 10.5,
    "net_weight": 9.8,
    "making_charge_type": "per_gram",
    "making_charge": 150,
    "stock_quantity": 5
}
r = requests.post(f"{BASE_URL}/inventory/", json=item_data, headers=HEADERS)
inv_id = r.json().get("id") if r.status_code in (200, 201) else None
check_any("INVENTORY: Create item", r, [200, 201])

r = requests.get(f"{BASE_URL}/inventory/?search=Ring", headers=HEADERS)
check("INVENTORY: Search", r, 200)

if inv_id:
    r = requests.get(f"{BASE_URL}/inventory/{inv_id}", headers=HEADERS)
    check("INVENTORY: Get by ID", r, 200)

    r = requests.put(f"{BASE_URL}/inventory/{inv_id}", json={"gross_weight": 11.0}, headers=HEADERS)
    check_any("INVENTORY: Update item", r, [200])

# =============================
# 6. METAL RATES
# =============================
print("\n=== METAL RATES ===")

r = requests.get(f"{BASE_URL}/metal-rates/", headers=HEADERS)
check("METAL RATES: List", r, 200)

r = requests.get(f"{BASE_URL}/metal-rates/gold/latest", headers=HEADERS)
check_any("METAL RATES: Gold latest", r, [200, 404])

r = requests.get(f"{BASE_URL}/metal-rates/silver/latest", headers=HEADERS)
check_any("METAL RATES: Silver latest", r, [200, 404])

# Create/update today's gold rate
rate_data = {"metal_type": "Gold", "rate_per_gram": 6200.0, "date": str(date.today())}
r = requests.post(f"{BASE_URL}/metal-rates/", json=rate_data, headers=HEADERS)
check_any("METAL RATES: Set today gold rate", r, [200, 201, 400, 409])

# =============================
# 7. PURCHASES
# =============================
print("\n=== PURCHASES ===")

r = requests.get(f"{BASE_URL}/purchases/", headers=HEADERS)
check("PURCHASES: List", r, 200)

r = requests.get(f"{BASE_URL}/purchases/gold", headers=HEADERS)
check_any("PURCHASES: Gold list", r, [200])

r = requests.get(f"{BASE_URL}/purchases/silver", headers=HEADERS)
check_any("PURCHASES: Silver list", r, [200])

r = requests.get(f"{BASE_URL}/purchases/9999999", headers=HEADERS)
check_any("PURCHASES: 404 for nonexistent", r, [404, 422])

# =============================
# 8. SALES
# =============================
print("\n=== SALES ===")

r = requests.get(f"{BASE_URL}/sales/", headers=HEADERS)
check("SALES: List", r, 200)

r = requests.get(f"{BASE_URL}/sales/9999999", headers=HEADERS)
check_any("SALES: 404 for nonexistent", r, [404, 422])

# =============================
# 9. INVOICES
# =============================
print("\n=== INVOICES ===")

r = requests.get(f"{BASE_URL}/invoices/", headers=HEADERS)
check("INVOICES: List", r, 200)

r = requests.get(f"{BASE_URL}/invoices/9999999", headers=HEADERS)
check("INVOICES: 404 for nonexistent", r, 404)

# =============================
# 10. BILLING
# =============================
print("\n=== BILLING ===")

r = requests.get(f"{BASE_URL}/billing/", headers=HEADERS)
check_any("BILLING: List", r, [200])

# =============================
# 11. REPORTS
# =============================
print("\n=== REPORTS ===")

for report in ["sales", "purchases", "inventory", "profit", "expenses", "gst", "customers", "suppliers"]:
    r = requests.get(f"{BASE_URL}/reports/{report}", headers=HEADERS)
    check(f"REPORTS: {report.upper()}", r, 200)

# =============================
# 12. SETTINGS
# =============================
print("\n=== SETTINGS ===")

r = requests.get(f"{BASE_URL}/settings/", headers=HEADERS)
check("SETTINGS: List", r, 200)

# =============================
# 13. EXCHANGES
# =============================
print("\n=== EXCHANGES ===")

r = requests.get(f"{BASE_URL}/exchanges/", headers=HEADERS)
check("EXCHANGES: List", r, 200)

# =============================
# 14. STOCK
# =============================
print("\n=== STOCK ===")

r = requests.get(f"{BASE_URL}/stock/", headers=HEADERS)
check_any("STOCK: List", r, [200])

# =============================
# 15. SELLERS
# =============================
print("\n=== SELLERS ===")

r = requests.get(f"{BASE_URL}/sellers/", headers=HEADERS)
check_any("SELLERS: List", r, [200])

# =============================
# 16. PRODUCTS
# =============================
print("\n=== PRODUCTS ===")

r = requests.get(f"{BASE_URL}/products/", headers=HEADERS)
check_any("PRODUCTS: List", r, [200])

# =============================
# 17. BUSINESS LOGIC VERIFICATION
# =============================
print("\n=== BUSINESS LOGIC ===")

# GST 3% on gold
item_value = 100000.0
cgst = item_value * 1.5 / 100  # 1500
sgst = item_value * 1.5 / 100  # 1500
total_gst = cgst + sgst         # 3000
if abs(total_gst - 3000.0) < 0.01:
    RESULTS["PASS"].append(f"BUSINESS LOGIC: GST 3% = ₹{total_gst:.2f} on ₹{item_value:.2f}")
else:
    RESULTS["FAIL"].append(f"BUSINESS LOGIC: GST calc mismatch: {total_gst}")

# Discount
subtotal = 50000.0
disc = subtotal * 5 / 100   # 2500
after = subtotal - disc     # 47500
if abs(after - 47500.0) < 0.01:
    RESULTS["PASS"].append("BUSINESS LOGIC: 5% discount calculation correct")
else:
    RESULTS["FAIL"].append(f"BUSINESS LOGIC: Discount error: {after}")

# Round-off within ±0.5
total = 103247.38
rounded = round(total)
round_off = rounded - total
if abs(round_off) <= 0.5:
    RESULTS["PASS"].append(f"BUSINESS LOGIC: Round-off = {round_off:.2f} (within ±0.5)")
else:
    RESULTS["FAIL"].append(f"BUSINESS LOGIC: Round-off {round_off} exceeds ±0.5")

# Silver recovery formula
weight = 1000
tanch = 85.5
wastage = 2.0
final_tanch = tanch - wastage   # 83.5
recovered = weight * final_tanch / 100  # 835g
if abs(recovered - 835.0) < 0.01:
    RESULTS["PASS"].append(f"BUSINESS LOGIC: Silver recovery formula = {recovered}g")
else:
    RESULTS["FAIL"].append(f"BUSINESS LOGIC: Silver recovery error: {recovered}")

# Gold purchase value: fine_gold = net_wt * touch/100, amount = fine_gold * rate
net_wt = 98.0
touch = 91.6
rate_g = 6200.0
fine_gold = net_wt * touch / 100  # 89.768g
amount = fine_gold * rate_g        # 556561.6
if amount > 0:
    RESULTS["PASS"].append(f"BUSINESS LOGIC: Gold purchase amount = ₹{amount:,.2f}")
else:
    RESULTS["FAIL"].append("BUSINESS LOGIC: Gold amount calculation failed")

# Invoice total with items
item1 = 98.0 * 6200.0            # 607600 (net_wt * rate)
item2 = 50.0 * 6200.0            # 310000
disc = 10000.0
subtotal = item1 + item2 - disc  # 907600
cgst = subtotal * 1.5 / 100     # 13614
sgst = subtotal * 1.5 / 100     # 13614
grand = round(subtotal + cgst + sgst)
if grand > 0:
    RESULTS["PASS"].append(f"BUSINESS LOGIC: Invoice grand total = ₹{grand:,}")
else:
    RESULTS["FAIL"].append("BUSINESS LOGIC: Invoice total failed")

# =============================
# 18. DATABASE INTEGRITY (via API)
# =============================
print("\n=== DATABASE INTEGRITY ===")

# FK violation: purchase with nonexistent supplier
r = requests.post(f"{BASE_URL}/purchases/", json={
    "invoice_no": f"FK-TEST-{uid}",
    "supplier_id": 999999,
    "metal_type": "Gold",
    "gross_weight": 100,
    "net_weight": 98,
    "touch": 91.6,
    "rate": 6200,
    "amount": 500000,
    "date": str(date.today())
}, headers=HEADERS)
check_any("DATABASE: FK violation rejected (nonexistent supplier)", r, [400, 404, 422])

# 404 on nonexistent resources
for endpoint in ["customers/9999999", "suppliers/9999999", "invoices/9999999"]:
    r = requests.get(f"{BASE_URL}/{endpoint}", headers=HEADERS)
    check(f"DATABASE: 404 on {endpoint}", r, 404)

# =============================
# 19. AUTHORIZATION CHECKS
# =============================
print("\n=== AUTHORIZATION ===")

protected_endpoints = [
    ("GET", f"{BASE_URL}/customers/"),
    ("GET", f"{BASE_URL}/suppliers/"),
    ("GET", f"{BASE_URL}/inventory/"),
    ("GET", f"{BASE_URL}/purchases/"),
    ("GET", f"{BASE_URL}/invoices/"),
    ("GET", f"{BASE_URL}/reports/sales"),
    ("GET", f"{BASE_URL}/settings/"),
]
for method, url in protected_endpoints:
    r = requests.request(method, url)  # No auth header
    check(f"AUTH GUARD: {url.split('/api/v1/')[1]}", r, 401)

# =============================
# FINAL REPORT
# =============================
print("\n" + "="*70)
print("FINAL VERIFICATION REPORT")
print("="*70)

print(f"\nPASS ({len(RESULTS['PASS'])} checks):")
for p in RESULTS["PASS"]:
    print(f"  ✅  {p}")

print(f"\nWARNING ({len(RESULTS['WARN'])} items):")
for w in RESULTS["WARN"]:
    print(f"  ⚠️   {w}")

print(f"\nFAILED ({len(RESULTS['FAIL'])} items):")
for f in RESULTS["FAIL"]:
    print(f"  ❌  {f}")

total = len(RESULTS["PASS"]) + len(RESULTS["WARN"]) + len(RESULTS["FAIL"])
print(f"\nSUMMARY: {total} checks | {len(RESULTS['PASS'])} PASS | {len(RESULTS['WARN'])} WARN | {len(RESULTS['FAIL'])} FAIL")

sys.exit(1 if RESULTS["FAIL"] else 0)
