#!/usr/bin/env python3
"""
Comprehensive API Endpoint Verification Script
Tests all endpoints for correct status codes, response schemas, validation, and authorization
"""

import sys
import requests
from typing import Dict, List, Any
import json

BASE_URL = "http://localhost:8000"
api = "/api/v1"

# Colors for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

class APIVerifier:
    def __init__(self):
        self.token = None
        self.passed = []
        self.failed = []
        self.warnings = []
        
    def log_pass(self, msg: str):
        self.passed.append(msg)
        print(f"{GREEN}✓ PASS{RESET}: {msg}")
        
    def log_fail(self, msg: str, details: str = ""):
        self.failed.append(f"{msg} | {details}")
        print(f"{RED}✗ FAIL{RESET}: {msg}")
        if details:
            print(f"  Details: {details}")
            
    def log_warn(self, msg: str):
        self.warnings.append(msg)
        print(f"{YELLOW}⚠ WARN{RESET}: {msg}")

    def authenticate(self):
        """Authenticate and get token"""
        print("\n=== AUTHENTICATION ===")
        try:
            # Login
            response = requests.post(
                f"{BASE_URL}{api}/auth/login",
                data={"username": "admin", "password": "admin123"}
            )
            if response.status_code == 200:
                data = response.json()
                if "access_token" in data:
                    self.token = data["access_token"]
                    self.log_pass("Authentication: Login successful")
                    return True
                else:
                    self.log_fail("Authentication: No access_token in response", str(data))
                    return False
            else:
                self.log_fail(f"Authentication: Login failed with status {response.status_code}", response.text[:200])
                return False
        except Exception as e:
            self.log_fail("Authentication: Exception during login", str(e))
            return False

    def get_headers(self, auth: bool = True) -> Dict[str, str]:
        """Get request headers"""
        headers = {"Content-Type": "application/json"}
        if auth and self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def verify_dashboard(self):
        """Verify Dashboard endpoints"""
        print("\n=== DASHBOARD ===")
        try:
            # Get metrics
            response = requests.get(f"{BASE_URL}{api}/dashboard/metrics", headers=self.get_headers())
            if response.status_code == 200:
                data = response.json()
                # Actual schema from ReportService
                required_keys = ["today_sales", "today_bills", "today_purchases", "today_profit", 
                               "total_customers", "inventory_items", "inventory_weight", "low_stock_count"]
                if all(k in data for k in required_keys):
                    self.log_pass("Dashboard: Metrics endpoint returns correct schema")
                else:
                    missing = [k for k in required_keys if k not in data]
                    self.log_fail("Dashboard: Missing keys in metrics response", f"Missing: {missing}, Got: {list(data.keys())}")
            else:
                self.log_fail(f"Dashboard: Metrics endpoint failed with status {response.status_code}", response.text[:200])
                
            # Get recent activity
            response = requests.get(f"{BASE_URL}{api}/dashboard/recent-activity", headers=self.get_headers())
            if response.status_code == 200:
                data = response.json()
                # Actual schema returns recent_bills and recent_purchases
                if "recent_bills" in data and "recent_purchases" in data:
                    self.log_pass("Dashboard: Recent activity endpoint returns correct schema")
                else:
                    self.log_fail("Dashboard: Missing keys in recent activity", f"Got: {list(data.keys())}")
            else:
                self.log_fail(f"Dashboard: Recent activity failed with status {response.status_code}", response.text[:200])
                
        except Exception as e:
            self.log_fail("Dashboard: Exception", str(e))

    def verify_customers(self):
        """Verify Customers endpoints"""
        print("\n=== CUSTOMERS ===")
        try:
            # List customers
            response = requests.get(f"{BASE_URL}{api}/customers/", headers=self.get_headers())
            if response.status_code == 200:
                self.log_pass("Customers: GET /customers/ returns 200")
            else:
                self.log_fail(f"Customers: GET /customers/ failed with status {response.status_code}", response.text[:200])
                
            # Create customer (using correct schema with first_name, last_name, phone_number)
            test_customer = {
                "first_name": "Test",
                "last_name": "Customer",
                "phone_number": "9999999999",
                "email": "testverify@example.com",
                "pan_card": None,
                "aadhar_card": None,
                "gst_number": None,
                "credit_limit": 0,
                "outstanding_balance": 0
            }
            response = requests.post(f"{BASE_URL}{api}/customers/", 
                                    json=test_customer, 
                                    headers=self.get_headers())
            if response.status_code in [200, 201]:
                customer_id = response.json().get("id")
                self.log_pass("Customers: POST /customers/ creates customer")
                
                # Get specific customer
                if customer_id:
                    response = requests.get(f"{BASE_URL}{api}/customers/{customer_id}", headers=self.get_headers())
                    if response.status_code == 200:
                        self.log_pass(f"Customers: GET /customers/{customer_id} returns 200")
                    else:
                        self.log_fail(f"Customers: GET /customers/{customer_id} failed", str(response.status_code))
                        
                    # Update customer
                    update_data = {"first_name": "Updated"}
                    response = requests.put(f"{BASE_URL}{api}/customers/{customer_id}", 
                                          json=update_data, 
                                          headers=self.get_headers())
                    if response.status_code == 200:
                        self.log_pass(f"Customers: PUT /customers/{customer_id} updates customer")
                    else:
                        self.log_fail(f"Customers: PUT /customers/{customer_id} failed", str(response.status_code))
                        
                    # Delete customer
                    response = requests.delete(f"{BASE_URL}{api}/customers/{customer_id}", headers=self.get_headers())
                    if response.status_code in [200, 204]:
                        self.log_pass(f"Customers: DELETE /customers/{customer_id} deletes customer")
                    else:
                        self.log_fail(f"Customers: DELETE /customers/{customer_id} failed", str(response.status_code))
            else:
                self.log_fail(f"Customers: POST /customers/ failed with status {response.status_code}", response.text[:200])
                
            # Test validation - missing required fields
            response = requests.post(f"{BASE_URL}{api}/customers/", 
                                    json={"first_name": "Test"}, 
                                    headers=self.get_headers())
            if response.status_code == 422:
                self.log_pass("Customers: Validation rejects missing required fields (422)")
            else:
                self.log_warn(f"Customers: Expected 422 for validation error, got {response.status_code}")
                
        except Exception as e:
            self.log_fail("Customers: Exception", str(e))

    def verify_suppliers(self):
        """Verify Suppliers endpoints"""
        print("\n=== SUPPLIERS ===")
        try:
            # List suppliers
            response = requests.get(f"{BASE_URL}{api}/suppliers/", headers=self.get_headers())
            if response.status_code == 200:
                self.log_pass("Suppliers: GET /suppliers/ returns 200")
            else:
                self.log_fail(f"Suppliers: GET /suppliers/ failed with status {response.status_code}", response.text[:200])
                
            # Create supplier
            test_supplier = {
                "name": "Test Supplier Verify",
                "mobile": "8888888888",
                "email": "supplierverify@example.com",
                "address": "Supplier Address",
                "city": "Supplier City",
                "state": "Supplier State",
                "pincode": "654321",
                "gstin": ""
            }
            response = requests.post(f"{BASE_URL}{api}/suppliers/", 
                                    json=test_supplier, 
                                    headers=self.get_headers())
            if response.status_code in [200, 201]:
                supplier_id = response.json().get("id")
                self.log_pass("Suppliers: POST /suppliers/ creates supplier")
                
                if supplier_id:
                    # Delete supplier
                    response = requests.delete(f"{BASE_URL}{api}/suppliers/{supplier_id}", headers=self.get_headers())
                    if response.status_code in [200, 204]:
                        self.log_pass(f"Suppliers: DELETE /suppliers/{supplier_id} deletes supplier")
            else:
                self.log_fail(f"Suppliers: POST /suppliers/ failed with status {response.status_code}", response.text[:200])
                
        except Exception as e:
            self.log_fail("Suppliers: Exception", str(e))

    def verify_inventory(self):
        """Verify Inventory endpoints"""
        print("\n=== INVENTORY ===")
        try:
            # List categories
            response = requests.get(f"{BASE_URL}{api}/inventory/categories", headers=self.get_headers())
            if response.status_code == 200:
                self.log_pass("Inventory: GET /inventory/categories returns 200")
            else:
                self.log_fail(f"Inventory: GET /inventory/categories failed with status {response.status_code}", response.text[:200])
                
            # List items
            response = requests.get(f"{BASE_URL}{api}/inventory/items", headers=self.get_headers())
            if response.status_code == 200:
                self.log_pass("Inventory: GET /inventory/items returns 200")
            else:
                self.log_fail(f"Inventory: GET /inventory/items failed with status {response.status_code}", response.text[:200])
                
        except Exception as e:
            self.log_fail("Inventory: Exception", str(e))

    def verify_purchases(self):
        """Verify Purchases endpoints"""
        print("\n=== PURCHASES ===")
        try:
            # List gold purchases
            response = requests.get(f"{BASE_URL}{api}/purchases/gold", headers=self.get_headers())
            if response.status_code == 200:
                self.log_pass("Purchases: GET /purchases/gold returns 200")
            else:
                self.log_fail(f"Purchases: GET /purchases/gold failed with status {response.status_code}", response.text[:200])
                
            # List silver purchases
            response = requests.get(f"{BASE_URL}{api}/purchases/silver", headers=self.get_headers())
            if response.status_code == 200:
                self.log_pass("Purchases: GET /purchases/silver returns 200")
            else:
                self.log_fail(f"Purchases: GET /purchases/silver failed with status {response.status_code}", response.text[:200])
                
        except Exception as e:
            self.log_fail("Purchases: Exception", str(e))

    def verify_sales(self):
        """Verify Sales endpoints"""
        print("\n=== SALES ===")
        try:
            # List sales
            response = requests.get(f"{BASE_URL}{api}/sales/", headers=self.get_headers())
            if response.status_code == 200:
                self.log_pass("Sales: GET /sales/ returns 200")
            else:
                self.log_fail(f"Sales: GET /sales/ failed with status {response.status_code}", response.text[:200])
                
        except Exception as e:
            self.log_fail("Sales: Exception", str(e))

    def verify_invoices(self):
        """Verify Invoices endpoints"""
        print("\n=== INVOICES ===")
        try:
            # List invoices
            response = requests.get(f"{BASE_URL}{api}/invoices/", headers=self.get_headers())
            if response.status_code == 200:
                self.log_pass("Invoices: GET /invoices/ returns 200")
            else:
                self.log_fail(f"Invoices: GET /invoices/ failed with status {response.status_code}", response.text[:200])
                
        except Exception as e:
            self.log_fail("Invoices: Exception", str(e))

    def verify_reports(self):
        """Verify Reports endpoints"""
        print("\n=== REPORTS ===")
        try:
            # Sales report
            response = requests.get(f"{BASE_URL}{api}/reports/sales", headers=self.get_headers())
            if response.status_code == 200:
                self.log_pass("Reports: GET /reports/sales returns 200")
            else:
                self.log_fail(f"Reports: GET /reports/sales failed with status {response.status_code}", response.text[:200])
                
            # Purchases report
            response = requests.get(f"{BASE_URL}{api}/reports/purchases", headers=self.get_headers())
            if response.status_code == 200:
                self.log_pass("Reports: GET /reports/purchases returns 200")
            else:
                self.log_fail(f"Reports: GET /reports/purchases failed with status {response.status_code}", response.text[:200])
                
            # Inventory report
            response = requests.get(f"{BASE_URL}{api}/reports/inventory", headers=self.get_headers())
            if response.status_code == 200:
                self.log_pass("Reports: GET /reports/inventory returns 200")
            else:
                self.log_fail(f"Reports: GET /reports/inventory failed with status {response.status_code}", response.text[:200])
                
        except Exception as e:
            self.log_fail("Reports: Exception", str(e))

    def verify_settings(self):
        """Verify Settings endpoints"""
        print("\n=== SETTINGS ===")
        try:
            # Get settings
            response = requests.get(f"{BASE_URL}{api}/settings/", headers=self.get_headers())
            if response.status_code == 200:
                self.log_pass("Settings: GET /settings/ returns 200")
            else:
                self.log_fail(f"Settings: GET /settings/ failed with status {response.status_code}", response.text[:200])
                
        except Exception as e:
            self.log_fail("Settings: Exception", str(e))

    def verify_metal_rates(self):
        """Verify Metal Rates endpoints"""
        print("\n=== METAL RATES ===")
        try:
            # Get latest rates (correct endpoint)
            response = requests.get(f"{BASE_URL}{api}/metal-rates/latest", headers=self.get_headers())
            if response.status_code == 200:
                self.log_pass("Metal Rates: GET /metal-rates/latest returns 200")
            else:
                self.log_fail(f"Metal Rates: GET /metal-rates/latest failed with status {response.status_code}", response.text[:200])
                
        except Exception as e:
            self.log_fail("Metal Rates: Exception", str(e))

    def verify_authorization(self):
        """Verify authorization is enforced"""
        print("\n=== AUTHORIZATION ===")
        try:
            # Try accessing protected endpoint without token
            response = requests.get(f"{BASE_URL}{api}/customers/", headers={"Content-Type": "application/json"})
            if response.status_code == 401:
                self.log_pass("Authorization: Protected endpoints reject requests without token (401)")
            else:
                self.log_fail(f"Authorization: Expected 401 for no token, got {response.status_code}", response.text[:200])
                
            # Try with invalid token
            headers = {
                "Content-Type": "application/json",
                "Authorization": "Bearer invalid_token_12345"
            }
            response = requests.get(f"{BASE_URL}{api}/customers/", headers=headers)
            if response.status_code == 401:
                self.log_pass("Authorization: Protected endpoints reject invalid token (401)")
            else:
                self.log_fail(f"Authorization: Expected 401 for invalid token, got {response.status_code}", response.text[:200])
                
        except Exception as e:
            self.log_fail("Authorization: Exception", str(e))

    def print_summary(self):
        """Print verification summary"""
        print("\n" + "="*70)
        print("VERIFICATION SUMMARY")
        print("="*70)
        print(f"\n{GREEN}PASSED: {len(self.passed)}{RESET}")
        for msg in self.passed:
            print(f"  ✓ {msg}")
            
        if self.warnings:
            print(f"\n{YELLOW}WARNINGS: {len(self.warnings)}{RESET}")
            for msg in self.warnings:
                print(f"  ⚠ {msg}")
            
        if self.failed:
            print(f"\n{RED}FAILED: {len(self.failed)}{RESET}")
            for msg in self.failed:
                print(f"  ✗ {msg}")
            
        print("\n" + "="*70)
        total = len(self.passed) + len(self.failed)
        pass_rate = (len(self.passed) / total * 100) if total > 0 else 0
        print(f"Pass Rate: {pass_rate:.1f}% ({len(self.passed)}/{total})")
        print("="*70 + "\n")
        
        return len(self.failed) == 0

def main():
    print("="*70)
    print("API ENDPOINT VERIFICATION")
    print("="*70)
    print(f"Base URL: {BASE_URL}")
    print(f"Testing against: {BASE_URL}{api}")
    print("="*70)
    
    verifier = APIVerifier()
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        print(f"\n{GREEN}✓{RESET} Server is running")
    except:
        print(f"\n{RED}✗{RESET} Server is not running at {BASE_URL}")
        print("Please start the backend server first:")
        print("  cd jewellery-erp/backend")
        print("  uvicorn app.main:app --reload")
        return 1
    
    # Run all verifications
    if not verifier.authenticate():
        print("\nAuthentication failed. Cannot proceed with other tests.")
        return 1
        
    verifier.verify_dashboard()
    verifier.verify_customers()
    verifier.verify_suppliers()
    verifier.verify_inventory()
    verifier.verify_purchases()
    verifier.verify_sales()
    verifier.verify_invoices()
    verifier.verify_reports()
    verifier.verify_settings()
    verifier.verify_metal_rates()
    verifier.verify_authorization()
    
    # Print summary
    success = verifier.print_summary()
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
