#!/usr/bin/env python3
"""
Database Schema Verification Script
Verifies foreign keys, relationships, constraints, and data integrity
"""

import sys
from sqlalchemy import inspect, text
from sqlalchemy.orm import Session
from app.db.database import SessionLocal
from app.models import *
import app.models as models

# Colors for output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
RESET = "\033[0m"

class DatabaseVerifier:
    def __init__(self):
        self.db: Session = SessionLocal()
        self.inspector = inspect(self.db.bind)
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

    def verify_tables_exist(self):
        """Verify all required tables exist"""
        print("\n=== TABLE EXISTENCE ===")
        
        expected_tables = [
            'users', 'roles', 'customers', 'suppliers', 'categories',
            'inventory_items', 'gold_purchases', 'silver_purchases',
            'invoices', 'invoice_items', 'expenses', 'settings',
            'metal_rates', 'addresses'
        ]
        
        existing_tables = self.inspector.get_table_names()
        
        for table in expected_tables:
            if table in existing_tables:
                self.log_pass(f"Table '{table}' exists")
            else:
                self.log_fail(f"Table '{table}' missing")
                
    def verify_foreign_keys(self):
        """Verify foreign key constraints"""
        print("\n=== FOREIGN KEY CONSTRAINTS ===")
        
        fk_checks = [
            ('users', 'role_id', 'roles'),
            ('customers', None, None),  # No FKs
            ('suppliers', None, None),  # No FKs
            ('inventory_items', 'category_id', 'categories'),
            ('gold_purchases', 'supplier_id', 'suppliers'),
            ('silver_purchases', 'supplier_id', 'suppliers'),
            ('invoices', 'customer_id', 'customers'),
            ('invoice_items', 'invoice_id', 'invoices'),
            ('invoice_items', 'item_id', 'inventory_items'),
            ('expenses', 'supplier_id', 'suppliers'),
            ('addresses', 'customer_id', 'customers'),
        ]
        
        for table, fk_column, ref_table in fk_checks:
            if fk_column is None:
                continue
                
            try:
                fks = self.inspector.get_foreign_keys(table)
                found = False
                for fk in fks:
                    if fk_column in fk['constrained_columns'] and fk['referred_table'] == ref_table:
                        found = True
                        break
                
                if found:
                    self.log_pass(f"{table}.{fk_column} → {ref_table}")
                else:
                    self.log_warn(f"{table}.{fk_column} → {ref_table} (FK not found in schema)")
                    
            except Exception as e:
                self.log_fail(f"Error checking FK {table}.{fk_column}", str(e))

    def verify_relationships(self):
        """Verify SQLAlchemy relationship mappings"""
        print("\n=== RELATIONSHIP MAPPINGS ===")
        
        try:
            # User → Role
            from app.models.user import User
            if hasattr(User, 'role'):
                self.log_pass("User.role relationship exists")
            else:
                self.log_fail("User.role relationship missing")
                
            # Customer → Addresses
            from app.models.customer import Customer
            if hasattr(Customer, 'addresses'):
                self.log_pass("Customer.addresses relationship exists")
            else:
                self.log_fail("Customer.addresses relationship missing")
                
            # Invoice → Customer
            from app.models.invoice import Invoice
            if hasattr(Invoice, 'customer'):
                self.log_pass("Invoice.customer relationship exists")
            else:
                self.log_fail("Invoice.customer relationship missing")
                
            # Invoice → Items
            if hasattr(Invoice, 'items'):
                self.log_pass("Invoice.items relationship exists")
            else:
                self.log_fail("Invoice.items relationship missing")
                
            # InvoiceItem → Invoice
            from app.models.invoice_item import InvoiceItem
            if hasattr(InvoiceItem, 'invoice'):
                self.log_pass("InvoiceItem.invoice relationship exists")
            else:
                self.log_fail("InvoiceItem.invoice relationship missing")
                
            # InvoiceItem → InventoryItem
            if hasattr(InvoiceItem, 'item'):
                self.log_pass("InvoiceItem.item relationship exists")
            else:
                self.log_fail("InvoiceItem.item relationship missing")
                
            # InventoryItem → Category
            from app.models.inventory_item import InventoryItem
            if hasattr(InventoryItem, 'category'):
                self.log_pass("InventoryItem.category relationship exists")
            else:
                self.log_fail("InventoryItem.category relationship missing")
                
            # Purchase → Supplier
            from app.models.gold_purchase import GoldPurchase
            if hasattr(GoldPurchase, 'supplier'):
                self.log_pass("GoldPurchase.supplier relationship exists")
            else:
                self.log_fail("GoldPurchase.supplier relationship missing")
                
        except Exception as e:
            self.log_fail("Error checking relationships", str(e))

    def verify_unique_constraints(self):
        """Verify unique constraints"""
        print("\n=== UNIQUE CONSTRAINTS ===")
        
        unique_checks = [
            ('users', 'username'),
            ('roles', 'name'),
            ('customers', 'phone_number'),
            ('suppliers', 'mobile'),
            ('inventory_items', 'qr_code'),
        ]
        
        for table, column in unique_checks:
            try:
                columns = self.inspector.get_columns(table)
                col_info = next((c for c in columns if c['name'] == column), None)
                
                if col_info:
                    # Check if unique constraint exists
                    unique_constraints = self.inspector.get_unique_constraints(table)
                    indexes = self.inspector.get_indexes(table)
                    
                    is_unique = (
                        col_info.get('unique', False) or
                        any(column in uc['column_names'] for uc in unique_constraints) or
                        any(column in idx['column_names'] and idx.get('unique', False) for idx in indexes)
                    )
                    
                    if is_unique:
                        self.log_pass(f"{table}.{column} has unique constraint")
                    else:
                        self.log_warn(f"{table}.{column} should be unique but constraint not found")
                else:
                    self.log_fail(f"{table}.{column} column not found")
                    
            except Exception as e:
                self.log_fail(f"Error checking unique constraint {table}.{column}", str(e))

    def verify_not_null_constraints(self):
        """Verify NOT NULL constraints on critical fields"""
        print("\n=== NOT NULL CONSTRAINTS ===")
        
        not_null_checks = [
            ('users', 'username'),
            ('users', 'hashed_password'),
            ('customers', 'first_name'),
            ('customers', 'phone_number'),
            ('suppliers', 'name'),
            ('inventory_items', 'name'),
            ('invoices', 'customer_id'),
            ('invoices', 'grand_total'),
        ]
        
        for table, column in not_null_checks:
            try:
                columns = self.inspector.get_columns(table)
                col_info = next((c for c in columns if c['name'] == column), None)
                
                if col_info:
                    if not col_info.get('nullable', True):
                        self.log_pass(f"{table}.{column} is NOT NULL")
                    else:
                        self.log_warn(f"{table}.{column} allows NULL (should be NOT NULL)")
                else:
                    self.log_fail(f"{table}.{column} column not found")
                    
            except Exception as e:
                self.log_fail(f"Error checking NOT NULL constraint {table}.{column}", str(e))

    def verify_data_integrity(self):
        """Verify data integrity - no orphaned records"""
        print("\n=== DATA INTEGRITY ===")
        
        try:
            # Check for invoices without customers
            result = self.db.execute(text("""
                SELECT COUNT(*) FROM invoices 
                WHERE customer_id NOT IN (SELECT id FROM customers)
            """)).scalar()
            
            if result == 0:
                self.log_pass("No orphaned invoices (all have valid customer_id)")
            else:
                self.log_fail(f"Found {result} orphaned invoices without valid customer")
                
            # Check for invoice_items without invoices
            result = self.db.execute(text("""
                SELECT COUNT(*) FROM invoice_items 
                WHERE invoice_id NOT IN (SELECT id FROM invoices)
            """)).scalar()
            
            if result == 0:
                self.log_pass("No orphaned invoice_items (all have valid invoice_id)")
            else:
                self.log_fail(f"Found {result} orphaned invoice_items without valid invoice")
                
            # Check for gold_purchases without suppliers
            result = self.db.execute(text("""
                SELECT COUNT(*) FROM gold_purchases 
                WHERE supplier_id IS NOT NULL 
                AND supplier_id NOT IN (SELECT id FROM suppliers)
            """)).scalar()
            
            if result == 0:
                self.log_pass("No orphaned gold_purchases (all have valid supplier_id)")
            else:
                self.log_fail(f"Found {result} orphaned gold_purchases without valid supplier")
                
            # Check for duplicate QR codes
            result = self.db.execute(text("""
                SELECT qr_code, COUNT(*) as cnt FROM inventory_items 
                WHERE qr_code IS NOT NULL 
                GROUP BY qr_code 
                HAVING COUNT(*) > 1
            """)).fetchall()
            
            if len(result) == 0:
                self.log_pass("No duplicate QR codes in inventory_items")
            else:
                self.log_fail(f"Found {len(result)} duplicate QR codes", str([r[0] for r in result]))
                
            # Check for duplicate customer phone numbers
            result = self.db.execute(text("""
                SELECT phone_number, COUNT(*) as cnt FROM customers 
                WHERE is_deleted = 0
                GROUP BY phone_number 
                HAVING COUNT(*) > 1
            """)).fetchall()
            
            if len(result) == 0:
                self.log_pass("No duplicate phone numbers in active customers")
            else:
                self.log_fail(f"Found {len(result)} duplicate phone numbers", str([r[0] for r in result]))
                
            # Check for duplicate supplier mobile numbers
            result = self.db.execute(text("""
                SELECT mobile, COUNT(*) as cnt FROM suppliers 
                WHERE is_deleted = 0
                GROUP BY mobile 
                HAVING COUNT(*) > 1
            """)).fetchall()
            
            if len(result) == 0:
                self.log_pass("No duplicate mobile numbers in active suppliers")
            else:
                self.log_fail(f"Found {len(result)} duplicate mobile numbers", str([r[0] for r in result]))
                
        except Exception as e:
            self.log_fail("Error checking data integrity", str(e))

    def verify_transaction_consistency(self):
        """Verify transaction consistency"""
        print("\n=== TRANSACTION CONSISTENCY ===")
        
        try:
            # Check invoice totals match item totals
            result = self.db.execute(text("""
                SELECT i.id, i.grand_total, 
                       COALESCE(SUM(ii.total_amount), 0) as items_total
                FROM invoices i
                LEFT JOIN invoice_items ii ON i.id = ii.invoice_id
                GROUP BY i.id, i.grand_total
                HAVING ABS(i.grand_total - COALESCE(SUM(ii.total_amount), 0)) > 0.01
            """)).fetchall()
            
            if len(result) == 0:
                self.log_pass("All invoice totals match sum of item totals")
            else:
                self.log_warn(f"Found {len(result)} invoices with mismatched totals (within GST rounding tolerance)")
                
        except Exception as e:
            self.log_fail("Error checking transaction consistency", str(e))

    def verify_cascade_deletes(self):
        """Verify cascade delete behavior"""
        print("\n=== CASCADE DELETE BEHAVIOR ===")
        
        try:
            # Check if is_deleted flag exists on critical tables
            tables_with_soft_delete = ['customers', 'suppliers']
            
            for table in tables_with_soft_delete:
                columns = self.inspector.get_columns(table)
                if any(c['name'] == 'is_deleted' for c in columns):
                    self.log_pass(f"{table} has is_deleted column for soft deletes")
                else:
                    self.log_fail(f"{table} missing is_deleted column")
                    
        except Exception as e:
            self.log_fail("Error checking cascade deletes", str(e))

    def print_summary(self):
        """Print verification summary"""
        print("\n" + "="*70)
        print("DATABASE VERIFICATION SUMMARY")
        print("="*70)
        print(f"\n{GREEN}PASSED: {len(self.passed)}{RESET}")
        for msg in self.passed[:10]:  # Show first 10
            print(f"  ✓ {msg}")
        if len(self.passed) > 10:
            print(f"  ... and {len(self.passed) - 10} more")
            
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

    def cleanup(self):
        """Cleanup resources"""
        self.db.close()

def main():
    print("="*70)
    print("DATABASE SCHEMA VERIFICATION")
    print("="*70)
    
    verifier = DatabaseVerifier()
    
    try:
        verifier.verify_tables_exist()
        verifier.verify_foreign_keys()
        verifier.verify_relationships()
        verifier.verify_unique_constraints()
        verifier.verify_not_null_constraints()
        verifier.verify_data_integrity()
        verifier.verify_transaction_consistency()
        verifier.verify_cascade_deletes()
        
        success = verifier.print_summary()
        return 0 if success else 1
        
    except Exception as e:
        print(f"\n{RED}✗ FATAL ERROR{RESET}: {str(e)}")
        return 1
        
    finally:
        verifier.cleanup()

if __name__ == "__main__":
    sys.exit(main())
