from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import FileResponse
from starlette.background import BackgroundTask
from typing import Any, Optional
import os
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import text, inspect
from app.core.config import settings
import numpy as np
from app.api.dependencies import require_tenant_id, get_db, get_current_user, RoleChecker
from app.models.user import User
from app.models.store import Store
from app.models.invoice import Invoice
from app.models.invoice_item import InvoiceItem
from app.models.gold_calculation import GoldCalculation
from app.models.silver_calculation import SilverCalculation
from app.models.purchase import Purchase
from app.models.purchase_item import PurchaseItem
from app.models.customer import Customer
from app.models.seller import Seller
from app.models.customer_ledger import CustomerLedger
from app.models.supplier_ledger import SupplierLedger
from app.models.exchange import Exchange
from app.models.exchange_item import ExchangeItem
from app.models.inventory_item import InventoryItem
from app.models.stock_item import StockItem
from app.models.expense import Expense
from app.models.metal_rates import MetalRate
from app.models.setting import Setting
import uuid
import time
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.exceptions import InvalidTag

router = APIRouter()

MAGIC_BACKUP_HEADER = b"JEWELLERY_ERP_ENCRYPTED_BACKUP_V1:"
PBKDF2_ITERATIONS = 100_000

def get_backup_key() -> str:
    """Retrieve the authoritative backup encryption key."""
    key = getattr(settings, "BACKUP_ENCRYPTION_KEY", None)
    if not key or not str(key).strip():
        key = getattr(settings, "SECRET_KEY", None)
    if not key or not str(key).strip():
        raise RuntimeError("No backup encryption key configured.")
    return str(key).strip()

def derive_backup_key(passphrase: str, salt: bytes) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
    )
    return kdf.derive(passphrase.encode("utf-8"))

def encrypt_backup_payload(plaintext_bytes: bytes, key: str) -> bytes:
    salt = os.urandom(16)
    derived = derive_backup_key(key, salt)
    aesgcm = AESGCM(derived)
    nonce = os.urandom(12)
    ciphertext = aesgcm.encrypt(nonce, plaintext_bytes, associated_data=MAGIC_BACKUP_HEADER)
    return MAGIC_BACKUP_HEADER + salt + nonce + ciphertext

def decrypt_backup_payload(encrypted_bytes: bytes, key: str) -> bytes:
    if not encrypted_bytes.startswith(MAGIC_BACKUP_HEADER):
        raise ValueError("Invalid backup format: missing authenticated header.")
    header_len = len(MAGIC_BACKUP_HEADER)
    if len(encrypted_bytes) < header_len + 16 + 12 + 16:
        raise ValueError("Invalid backup data: payload is truncated or incomplete.")
    salt = encrypted_bytes[header_len:header_len + 16]
    nonce = encrypted_bytes[header_len + 16:header_len + 28]
    ciphertext = encrypted_bytes[header_len + 28:]
    derived = derive_backup_key(key, salt)
    aesgcm = AESGCM(derived)
    try:
        return aesgcm.decrypt(nonce, ciphertext, associated_data=MAGIC_BACKUP_HEADER)
    except InvalidTag:
        raise ValueError("Decryption failed: incorrect key or corrupted/tampered backup.")

def _cleanup_stale_backups(backup_dir: str, max_age_seconds: int = 3600):
    """Clean up old backup and temporary files older than max_age_seconds (default 1 hr)."""
    try:
        now = time.time()
        for fname in os.listdir(backup_dir):
            fpath = os.path.join(backup_dir, fname)
            if os.path.isfile(fpath):
                if fname.startswith("tmp_") or (now - os.path.getmtime(fpath) > max_age_seconds):
                    try:
                        os.remove(fpath)
                    except Exception:
                        pass
    except Exception:
        pass

def _safe_float(val, default=0.0):
    if val is None:
        return default
    try:
        return float(val)
    except (ValueError, TypeError):
        return default

def _safe_str(val, default=""):
    if val is None:
        return default
    return str(val).strip()

def _get_safe_store_slug(store: Any, store_id: int) -> str:
    import re
    raw_name = (store.name if store and store.name else f"store_{store_id}").strip().lower()
    clean = re.sub(r'[^a-z0-9_-]', '_', raw_name)
    clean = re.sub(r'_+', '_', clean).strip('_')
    return clean or f"store_{store_id}"

def _get_tenant_queries(store_id: int):
    sid = int(store_id)
    return {
        'invoices': f"SELECT * FROM invoices WHERE store_id = {sid}",
        'invoice_items': f"SELECT * FROM invoice_items WHERE invoice_id IN (SELECT id FROM invoices WHERE store_id = {sid})",
        'gold_calculations': f"SELECT * FROM gold_calculations WHERE invoice_item_id IN (SELECT id FROM invoice_items WHERE invoice_id IN (SELECT id FROM invoices WHERE store_id = {sid}))",
        'silver_calculations': f"SELECT * FROM silver_calculations WHERE invoice_item_id IN (SELECT id FROM invoice_items WHERE invoice_id IN (SELECT id FROM invoices WHERE store_id = {sid}))",
        'purchases': f"SELECT * FROM purchases WHERE store_id = {sid}",
        'purchase_items': f"SELECT * FROM purchase_items WHERE purchase_id IN (SELECT id FROM purchases WHERE store_id = {sid})",
        'exchanges': f"SELECT * FROM exchanges WHERE store_id = {sid}",
        'exchange_items': f"SELECT * FROM exchange_items WHERE exchange_id IN (SELECT id FROM exchanges WHERE store_id = {sid})",
        'exchange_new_items': f"SELECT * FROM exchange_new_items WHERE exchange_id IN (SELECT id FROM exchanges WHERE store_id = {sid})",
        'customers': f"SELECT * FROM customers WHERE store_id = {sid}",
        'customer_ledgers': f"SELECT * FROM customer_ledgers WHERE customer_id IN (SELECT id FROM customers WHERE store_id = {sid})",
        'customer_addresses': f"SELECT * FROM customer_addresses WHERE customer_id IN (SELECT id FROM customers WHERE store_id = {sid})",
        'sellers': f"SELECT * FROM sellers WHERE store_id = {sid}",
        'supplier_ledgers': f"SELECT * FROM supplier_ledgers WHERE seller_id IN (SELECT id FROM sellers WHERE store_id = {sid})",
        'suppliers': f"SELECT * FROM suppliers WHERE store_id = {sid}",
        'stock_items': f"SELECT * FROM stock_items WHERE store_id = {sid}",
        'inventory': f"SELECT * FROM inventory WHERE store_id = {sid}",
        'expenses': f"SELECT * FROM expenses WHERE store_id = {sid}",
        'bills': f"SELECT * FROM bills WHERE store_id = {sid}",
        'bill_items': f"SELECT * FROM bill_items WHERE bill_id IN (SELECT id FROM bills WHERE store_id = {sid})",
        'payments': f"SELECT * FROM payments WHERE store_id = {sid}",
        'categories': f"SELECT * FROM categories WHERE store_id = {sid}",
        'stores': f"SELECT * FROM stores WHERE id = {sid}",
        'roles': "SELECT * FROM roles",
        'users': f"SELECT id, username, email, hashed_password, full_name, is_active, role_id, tenant_id, token_version FROM users WHERE tenant_id = {sid}",
        'settings': f"SELECT * FROM settings WHERE `key` LIKE 'store_{sid}_%%' OR `key` NOT LIKE 'store_%%'" if sid == 1 else f"SELECT * FROM settings WHERE `key` LIKE 'store_{sid}_%%'",
        'metal_rates': "SELECT * FROM metal_rates",
        'number_sequences': "SELECT * FROM number_sequences"
    }

@router.get("/download")
def download_backup(
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["Admin", "Shop Owner", "Manager"]))
):
    """Generate isolated, encrypted SQL backup for the current tenant's store."""
    import pandas as pd
    from app.db.database import engine

    store_id = require_tenant_id(current_user)
    store = db.query(Store).filter(Store.id == store_id).first()
    store_slug = _get_safe_store_slug(store, store_id)

    backup_dir = os.path.join(os.path.dirname(__file__), "..", "..", "backups")
    os.makedirs(backup_dir, exist_ok=True)
    _cleanup_stale_backups(backup_dir)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"{store_slug}_backup_{timestamp}.sql.enc"
    backup_path = os.path.join(backup_dir, backup_filename)
    
    try:
        tenant_queries = _get_tenant_queries(store_id)
        sql_lines = [
            "-- ==========================================================\n",
            "-- JEWELLERY ERP STORE BACKUP\n",
            f"-- Store ID: {store_id}\n",
            f"-- Store Name: {store.name if store else 'Unknown'}\n",
            f"-- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n",
            "-- ==========================================================\n\n",
            "SET FOREIGN_KEY_CHECKS=0;\n\n",
        ]

        for table_name, q in tenant_queries.items():
            try:
                df = pd.read_sql_query(q, engine)
            except Exception as tbl_err:
                # Never silently skip a table; fail the entire backup operation immediately
                raise RuntimeError(f"Export failed for table '{table_name}': {tbl_err}")

            if df.empty:
                continue

            sql_lines.append(f"-- ----------------------------------------------------------\n")
            sql_lines.append(f"-- Table: {table_name} ({len(df)} rows)\n")
            sql_lines.append(f"-- ----------------------------------------------------------\n")
            cols = [f"`{c}`" for c in df.columns]
            col_str = ", ".join(cols)
            
            for _, row in df.iterrows():
                vals = []
                for val in row:
                    if pd.isna(val) or val is None:
                        vals.append("NULL")
                    elif isinstance(val, (bool, np.bool_)):
                        vals.append("1" if val else "0")
                    elif isinstance(val, (int, float)):
                        vals.append(str(val))
                    else:
                        escaped = str(val).replace("'", "''").replace("\\", "\\\\")
                        vals.append(f"'{escaped}'")
                sql_lines.append(f"INSERT INTO `{table_name}` ({col_str}) VALUES ({', '.join(vals)});\n")
            sql_lines.append("\n")

        sql_lines.append("SET FOREIGN_KEY_CHECKS=1;\n")
        raw_sql_bytes = "".join(sql_lines).encode("utf-8")

        # Encrypt the SQL backup payload using authenticated AES-256-GCM
        backup_key = get_backup_key()
        encrypted_bytes = encrypt_backup_payload(raw_sql_bytes, backup_key)

        with open(backup_path, "wb") as f:
            f.write(encrypted_bytes)

    except HTTPException:
        if os.path.exists(backup_path):
            try:
                os.remove(backup_path)
            except Exception:
                pass
        raise
    except Exception as e:
        if os.path.exists(backup_path):
            try:
                os.remove(backup_path)
            except Exception:
                pass
        print(f"Backup failed: {type(e).__name__}")
        raise HTTPException(status_code=500, detail="Backup operation failed due to incomplete table export")
    
    return FileResponse(
        path=backup_path, 
        filename=backup_filename, 
        media_type='application/octet-stream',
        background=BackgroundTask(os.remove, backup_path)
    )

@router.post("/restore")
async def restore_backup(
    file: UploadFile = File(...),
    custom_key: Optional[str] = Form(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["Admin", "Shop Owner"]))
):
    """
    Restore tenant data from an authenticated, encrypted SQL backup file.
    Validates decryption authenticity, integrity tag, and tenant scoping.
    """
    store_id = require_tenant_id(current_user)
    key = (custom_key or "").strip() or get_backup_key()
    
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Uploaded backup file is empty.")

    try:
        sql_bytes = decrypt_backup_payload(contents, key)
        sql_text = sql_bytes.decode("utf-8")
    except ValueError as dec_err:
        raise HTTPException(
            status_code=400, 
            detail=f"Backup restoration failed: {str(dec_err)}"
        )
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Backup restoration failed: unable to decrypt backup."
        )

    # Validate tenant scope in backup header to prevent restoring another tenant's backup
    expected_tag = f"-- Store ID: {store_id}"
    if expected_tag not in sql_text:
        raise HTTPException(
            status_code=400,
            detail="Backup tenant mismatch: backup file does not belong to your store."
        )

    # Execute SQL statements safely within a transaction
    statements = [s.strip() for s in sql_text.split(";\n") if s.strip()]
    from app.db.database import engine
    try:
        with engine.connect() as conn:
            with conn.begin():
                for stmt in statements:
                    clean_stmt = "\n".join(
                        line for line in stmt.splitlines() if not line.strip().startswith("--")
                    ).strip()
                    if clean_stmt:
                        conn.execute(text(clean_stmt))
    except Exception as exec_err:
        raise HTTPException(
            status_code=500,
            detail="Failed to execute restored SQL statements safely."
        )

    return {
        "status": "success",
        "message": f"Backup restored successfully for store ID {store_id}.",
        "statements_executed": len(statements)
    }

@router.get("/excel-download")
def download_excel_backup(
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["Admin", "Shop Owner", "Manager"]))
):
    """Download ZIP of Excel files scoped exclusively to the current tenant."""
    import pandas as pd
    import zipfile
    from app.db.database import engine
    
    store_id = require_tenant_id(current_user)
    store = db.query(Store).filter(Store.id == store_id).first()
    store_slug = _get_safe_store_slug(store, store_id)

    backup_dir = os.path.join(os.path.dirname(__file__), "..", "..", "backups")
    os.makedirs(backup_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"{store_slug}_backup_{timestamp}.zip"
    zip_path = os.path.join(backup_dir, zip_filename)
    
    req_id = uuid.uuid4().hex
    _cleanup_stale_backups(backup_dir)
    excel_paths = []
    
    try:
        tenant_queries = _get_tenant_queries(store_id)
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for table_name, q in tenant_queries.items():
                try:
                    df = pd.read_sql_query(q, engine)
                    if df.empty:
                        continue
                    
                    # Convert datetimes to IST
                    for col in df.select_dtypes(include=['datetime64[ns, UTC]', 'datetime64[ns]']).columns:
                        try:
                            if df[col].dt.tz is None:
                                df[col] = df[col].dt.tz_localize('UTC').dt.tz_convert('Asia/Kolkata')
                            else:
                                df[col] = df[col].dt.tz_convert('Asia/Kolkata')
                            df[col] = df[col].dt.strftime('%Y-%m-%d %I:%M:%S %p')
                        except Exception:
                            pass

                    # Unique filename per request avoids concurrent race overwrites
                    table_excel_filename = f"{table_name}.xlsx"
                    temp_excel_filename = f"tmp_{req_id}_{table_name}.xlsx"
                    table_excel_path = os.path.join(backup_dir, temp_excel_filename)
                    df.to_excel(table_excel_path, index=False)
                    excel_paths.append(table_excel_path)
                    zipf.write(table_excel_path, arcname=table_excel_filename)
                except Exception as t_err:
                    raise RuntimeError(f"Excel export failed for table '{table_name}': {t_err}")
                
        if not excel_paths:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.writestr("empty_store.txt", f"No records found for store {store_id}.")
            
    except Exception as e:
        if os.path.exists(zip_path):
            try:
                os.remove(zip_path)
            except Exception:
                pass
        print(f"Excel Backup failed: {type(e).__name__}")
        raise HTTPException(status_code=500, detail="Excel Backup failed due to table export error")
    finally:
        for path in excel_paths:
            if os.path.exists(path):
                try:
                    os.remove(path)
                except Exception:
                    pass
    
    return FileResponse(
        path=zip_path, 
        filename=zip_filename, 
        media_type='application/zip',
        background=BackgroundTask(os.remove, zip_path)
    )

@router.get("/all-tables-excel")
def download_all_tables_single_excel(
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["Admin", "Shop Owner", "Manager"]))
):
    """Download single curated Excel workbook scoped exclusively to current tenant."""
    import pandas as pd
    import openpyxl
    from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
    from openpyxl.utils import get_column_letter

    store_id = require_tenant_id(current_user)
    store = db.query(Store).filter(Store.id == store_id).first()
    store_slug = _get_safe_store_slug(store, store_id)

    backup_dir = os.path.join(os.path.dirname(__file__), "..", "..", "backups")
    os.makedirs(backup_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    excel_filename = f"{store_slug}_master_{timestamp}.xlsx"
    excel_path = os.path.join(backup_dir, excel_filename)

    try:
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            
            # 1. Sales Invoices (Store Scoped)
            invoices = db.query(Invoice).filter(Invoice.store_id == store_id).order_by(Invoice.id.desc()).all()
            invoice_ids = [inv.id for inv in invoices]
            inv_rows = []
            for inv in invoices:
                c_name = f"{inv.customer.first_name} {inv.customer.last_name or ''}".strip() if inv.customer else "Walk-in Customer"
                c_phone = inv.customer.phone_number if inv.customer else ""
                inv_date_str = inv.invoice_date.strftime('%Y-%m-%d %I:%M %p') if inv.invoice_date else ""
                b_type = inv.bill_type.value if hasattr(inv.bill_type, 'value') else _safe_str(inv.bill_type, 'Cash')
                s_type = inv.settlement_type.value if hasattr(inv.settlement_type, 'value') else _safe_str(inv.settlement_type, 'Cash')
                status_str = inv.status.value if hasattr(inv.status, 'value') else _safe_str(inv.status, 'Completed')
                
                inv_rows.append({
                    'Invoice No': inv.invoice_number or f"INV-{inv.id}",
                    'Date': inv_date_str,
                    'Customer Name': c_name,
                    'Customer Phone': c_phone,
                    'Bill Type': b_type,
                    'Settlement Type': s_type,
                    'Taxable Subtotal (Rs)': _safe_float(inv.subtotal),
                    'GST Tax (Rs)': _safe_float(inv.tax_amount),
                    'Discount (Rs)': _safe_float(inv.discount_amount),
                    'Grand Total (Rs)': _safe_float(inv.grand_total),
                    'Cash Received (Rs)': _safe_float(inv.cash_received),
                    'Metal Received Value (Rs)': _safe_float(inv.metal_received_value),
                    'Balance Due (Rs)': _safe_float(inv.balance_amount),
                    'Gold Due (g)': _safe_float(inv.gold_balance_metal_weight),
                    'Silver Due (g)': _safe_float(inv.silver_balance_metal_weight),
                    'Status': status_str
                })
            if not inv_rows:
                inv_rows.append({'Invoice No': 'N/A', 'Date': '', 'Customer Name': 'No sales invoices recorded yet', 'Customer Phone': '', 'Bill Type': '', 'Settlement Type': '', 'Taxable Subtotal (Rs)': 0, 'GST Tax (Rs)': 0, 'Discount (Rs)': 0, 'Grand Total (Rs)': 0, 'Cash Received (Rs)': 0, 'Metal Received Value (Rs)': 0, 'Balance Due (Rs)': 0, 'Gold Due (g)': 0, 'Silver Due (g)': 0, 'Status': ''})
            pd.DataFrame(inv_rows).to_excel(writer, sheet_name='Sales_Invoices', index=False)

            # 2. Invoice Items (Store Scoped)
            items = db.query(InvoiceItem).filter(InvoiceItem.invoice_id.in_(invoice_ids)).order_by(InvoiceItem.id.desc()).all() if invoice_ids else []
            item_rows = []
            for it in items:
                inv = it.invoice
                c_name = f"{inv.customer.first_name} {inv.customer.last_name or ''}".strip() if (inv and inv.customer) else "Walk-in Customer"
                gc = db.query(GoldCalculation).filter(GoldCalculation.invoice_item_id == it.id).first()
                sc = db.query(SilverCalculation).filter(SilverCalculation.invoice_item_id == it.id).first()
                
                metal = 'GOLD' if gc else ('SILVER' if sc else _safe_str(it.item_type, ''))
                gross = _safe_float(gc.gross_weight) if gc else (_safe_float(sc.gross_weight) if sc else 0.0)
                stone = _safe_float(gc.stone_weight) if gc else (_safe_float(sc.stone_weight) if sc else 0.0)
                net = _safe_float(gc.net_weight) if gc else (_safe_float(sc.pure_weight) if sc else max(0.0, gross - stone))
                touch = _safe_float(gc.touch_purity) if gc else (_safe_float(sc.tanch_percentage) if sc else 0.0)
                wastage = _safe_float(gc.wastage) if gc else (_safe_float(sc.wastage) if sc else 0.0)
                rate = _safe_float(gc.applied_rate) if gc else (_safe_float(sc.applied_rate) if sc else 0.0)
                making = _safe_float(gc.making_charges_amount) if gc else (_safe_float(sc.making_charges_amount) if sc else 0.0)
                other = (_safe_float(gc.other_charges) + _safe_float(gc.hallmark_charges)) if gc else (_safe_float(sc.other_charges) if sc else 0.0)
                
                item_rows.append({
                    'Invoice No': inv.invoice_number if inv else '',
                    'Date': inv.invoice_date.strftime('%Y-%m-%d %I:%M %p') if (inv and inv.invoice_date) else '',
                    'Customer Name': c_name,
                    'Item Name': it.item_name or 'Item',
                    'Metal Type': metal,
                    'Gross Wt (g)': gross,
                    'Stone Wt (g)': stone,
                    'Net Wt (g)': net,
                    'Touch / Purity (%)': touch,
                    'Wastage (%)': wastage,
                    'Applied Rate (Rs)': rate,
                    'Making Charges (Rs)': making,
                    'Other Charges (Rs)': other,
                    'Item Final Amount (Rs)': _safe_float(it.final_price)
                })
            if not item_rows:
                item_rows.append({'Invoice No': 'N/A', 'Date': '', 'Customer Name': 'No invoice items recorded yet', 'Item Name': '', 'Metal Type': '', 'Gross Wt (g)': 0, 'Stone Wt (g)': 0, 'Net Wt (g)': 0, 'Touch / Purity (%)': 0, 'Wastage (%)': 0, 'Applied Rate (Rs)': 0, 'Making Charges (Rs)': 0, 'Other Charges (Rs)': 0, 'Item Final Amount (Rs)': 0})
            pd.DataFrame(item_rows).to_excel(writer, sheet_name='Invoice_Items', index=False)

            # 3. Purchases (Store Scoped)
            purchases = db.query(Purchase).filter(Purchase.store_id == store_id).order_by(Purchase.id.desc()).all()
            purchase_ids = [pur.id for pur in purchases]
            pur_rows = []
            for pur in purchases:
                s_name = pur.seller.name if pur.seller else 'Unknown Supplier'
                s_phone = (pur.seller.mobile if hasattr(pur.seller, 'mobile') else getattr(pur.seller, 'phone', '')) if pur.seller else ''
                status_str = pur.status.value if hasattr(pur.status, 'value') else _safe_str(pur.status, 'Completed')
                cash_p = _safe_float(pur.cash_paid)
                bal_due = _safe_float(pur.balance_amount) if pur.balance_amount is not None else (_safe_float(pur.grand_total) - cash_p)
                
                pur_rows.append({
                    'Purchase No': pur.purchase_number or f"PUR-{pur.id}",
                    'Date': pur.created_at.strftime('%Y-%m-%d %I:%M %p') if pur.created_at else '',
                    'Supplier Name': s_name,
                    'Supplier Phone': s_phone,
                    'Bill Type': pur.bill_type or 'Cash',
                    'Settlement Type': pur.settlement_type or 'Cash',
                    'Taxable Subtotal (Rs)': _safe_float(pur.total_taxable),
                    'CGST (Rs)': _safe_float(pur.cgst),
                    'SGST (Rs)': _safe_float(pur.sgst),
                    'Grand Total (Rs)': _safe_float(pur.grand_total),
                    'Cash Paid (Rs)': cash_p,
                    'Metal Given Value (Rs)': _safe_float(pur.metal_given_value),
                    'Balance Due (Rs)': bal_due,
                    'Gold Due (g)': _safe_float(pur.gold_balance_metal_weight),
                    'Silver Due (g)': _safe_float(pur.silver_balance_metal_weight),
                    'Status': status_str
                })
            if not pur_rows:
                pur_rows.append({'Purchase No': 'N/A', 'Date': '', 'Supplier Name': 'No purchases recorded yet', 'Supplier Phone': '', 'Bill Type': '', 'Settlement Type': '', 'Taxable Subtotal (Rs)': 0, 'CGST (Rs)': 0, 'SGST (Rs)': 0, 'Grand Total (Rs)': 0, 'Cash Paid (Rs)': 0, 'Metal Given Value (Rs)': 0, 'Balance Due (Rs)': 0, 'Gold Due (g)': 0, 'Silver Due (g)': 0, 'Status': ''})
            pd.DataFrame(pur_rows).to_excel(writer, sheet_name='Purchases', index=False)

            # 4. Purchase Items (Store Scoped)
            pur_items = db.query(PurchaseItem).filter(PurchaseItem.purchase_id.in_(purchase_ids)).order_by(PurchaseItem.id.desc()).all() if purchase_ids else []
            p_item_rows = []
            for pi in pur_items:
                pur = pi.purchase
                s_name = pur.seller.name if (pur and pur.seller) else ''
                p_item_rows.append({
                    'Purchase No': pur.purchase_number if pur else '',
                    'Date': pur.created_at.strftime('%Y-%m-%d %I:%M %p') if (pur and pur.created_at) else '',
                    'Supplier Name': s_name,
                    'Item Name': pi.item_name or 'Item',
                    'Metal Type': pi.metal_type or '',
                    'Category': pi.category or '',
                    'Gross Wt (g)': _safe_float(pi.gross_weight),
                    'Stone Wt (g)': _safe_float(pi.stone_weight),
                    'Net Wt (g)': _safe_float(pi.net_weight),
                    'Touch / Purity (%)': _safe_float(pi.touch_purity),
                    'Wastage (%)': _safe_float(pi.wastage),
                    'Fine Wt (g)': _safe_float(pi.fine_weight),
                    'Metal Rate (Rs)': _safe_float(pi.metal_rate),
                    'Labour Charge (Rs)': _safe_float(pi.labour_charge),
                    'Other Charges (Rs)': _safe_float(pi.other_charges) + _safe_float(pi.testing_melting_charge) + _safe_float(pi.hallmark_charge),
                    'Taxable Amount (Rs)': _safe_float(pi.taxable_amount)
                })
            if not p_item_rows:
                p_item_rows.append({'Purchase No': 'N/A', 'Date': '', 'Supplier Name': 'No purchase items recorded yet', 'Item Name': '', 'Metal Type': '', 'Category': '', 'Gross Wt (g)': 0, 'Stone Wt (g)': 0, 'Net Wt (g)': 0, 'Touch / Purity (%)': 0, 'Wastage (%)': 0, 'Fine Wt (g)': 0, 'Metal Rate (Rs)': 0, 'Labour Charge (Rs)': 0, 'Other Charges (Rs)': 0, 'Taxable Amount (Rs)': 0})
            pd.DataFrame(p_item_rows).to_excel(writer, sheet_name='Purchase_Items', index=False)

            # 5. Exchanges (Store Scoped)
            exchanges = db.query(Exchange).filter(Exchange.store_id == store_id).order_by(Exchange.id.desc()).all()
            exchange_ids = [exc.id for exc in exchanges]
            exc_rows = []
            for exc in exchanges:
                c_name = f"{exc.customer.first_name} {exc.customer.last_name or ''}".strip() if exc.customer else "Walk-in Customer"
                exc_dt = exc.exchange_date.strftime('%Y-%m-%d %I:%M %p') if hasattr(exc, 'exchange_date') and exc.exchange_date else (exc.created_at.strftime('%Y-%m-%d %I:%M %p') if hasattr(exc, 'created_at') and exc.created_at else '')
                exc_rows.append({
                    'Exchange No': f"EXC-{exc.id}",
                    'Date': exc_dt,
                    'Customer Name': c_name,
                    'Customer Phone': exc.customer.phone_number if exc.customer else '',
                    'New Items Total (Rs)': _safe_float(exc.total_new_value),
                    'Trade-in Metal Value (Rs)': _safe_float(exc.total_old_value),
                    'GST Tax (Rs)': _safe_float(exc.gst_amount),
                    'Grand Total (Rs)': _safe_float(exc.grand_total) if getattr(exc, 'grand_total', None) else (_safe_float(exc.total_new_value) + _safe_float(exc.gst_amount)),
                    'Net Difference (Rs)': _safe_float(exc.difference_amount),
                    'Amount Paid (Rs)': _safe_float(exc.amount_paid),
                    'Balance Amount (Rs)': _safe_float(exc.balance_amount),
                    'Gold Due (g)': _safe_float(exc.gold_balance_metal_weight),
                    'Silver Due (g)': _safe_float(exc.silver_balance_metal_weight),
                    'Settlement Type': _safe_str(exc.settlement_type, 'Cash')
                })
            if not exc_rows:
                exc_rows.append({'Exchange No': 'N/A', 'Date': '', 'Customer Name': 'No exchanges recorded yet', 'Customer Phone': '', 'New Items Total (Rs)': 0, 'Trade-in Metal Value (Rs)': 0, 'Net Difference (Rs)': 0, 'Amount Paid (Rs)': 0, 'Balance Amount (Rs)': 0, 'Gold Due (g)': 0, 'Silver Due (g)': 0, 'Settlement Type': ''})
            pd.DataFrame(exc_rows).to_excel(writer, sheet_name='Exchanges', index=False)

            # 6. Exchange Trade-in Items (Store Scoped)
            exc_items = db.query(ExchangeItem).filter(ExchangeItem.exchange_id.in_(exchange_ids)).order_by(ExchangeItem.id.desc()).all() if exchange_ids else []
            exc_item_rows = []
            for ei in exc_items:
                exc = ei.exchange
                c_name = f"{exc.customer.first_name} {exc.customer.last_name or ''}".strip() if (exc and exc.customer) else ""
                exc_dt = (exc.exchange_date.strftime('%Y-%m-%d %I:%M %p') if (exc and exc.exchange_date) else '')
                gross_w = _safe_float(ei.gross_weight)
                stone_w = _safe_float(ei.stone_weight)
                net_w = _safe_float(ei.net_weight) if ei.net_weight is not None else max(0.0, gross_w - stone_w)
                exc_item_rows.append({
                    'Exchange No': f"EXC-{exc.id}" if exc else '',
                    'Date': exc_dt,
                    'Customer Name': c_name,
                    'Old Item Name': ei.item_name or 'Old Metal',
                    'Metal Type': ei.metal or '',
                    'Purity / Touch (%)': _safe_float(ei.touch),
                    'Gross Wt (g)': gross_w,
                    'Stone Wt (g)': stone_w,
                    'Net Wt (g)': net_w,
                    'Fine Wt (g)': _safe_float(ei.fine_weight),
                    'Wastage (%)': _safe_float(ei.wastage),
                    'Rate Applied (Rs)': _safe_float(ei.rate_applied),
                    'Trade-in Value (Rs)': _safe_float(ei.calculated_value)
                })
            if not exc_item_rows:
                exc_item_rows.append({'Exchange No': 'N/A', 'Date': '', 'Customer Name': 'No trade-in items recorded yet', 'Old Item Name': '', 'Metal Type': '', 'Purity / Touch (%)': 0, 'Gross Wt (g)': 0, 'Stone Wt (g)': 0, 'Net Wt (g)': 0, 'Fine Wt (g)': 0, 'Wastage (%)': 0, 'Rate Applied (Rs)': 0, 'Trade-in Value (Rs)': 0})
            pd.DataFrame(exc_item_rows).to_excel(writer, sheet_name='Exchange_Items', index=False)

            # 7. Customers (Store Scoped)
            customers = db.query(Customer).filter(Customer.store_id == store_id).order_by(Customer.id.desc()).all()
            customer_ids = [c.id for c in customers]
            cust_rows = []
            for c in customers:
                bill_count = len(c.invoices) if hasattr(c, 'invoices') and c.invoices else 0
                c_bal = c.outstanding_balance if hasattr(c, 'outstanding_balance') else getattr(c, 'balance', 0)
                c_gold = c.fine_gold_balance if hasattr(c, 'fine_gold_balance') else getattr(c, 'gold_balance', 0)
                c_silver = c.fine_silver_balance if hasattr(c, 'fine_silver_balance') else getattr(c, 'silver_balance', 0)
                cust_rows.append({
                    'Customer ID': c.id,
                    'Customer Name': f"{c.first_name} {c.last_name or ''}".strip(),
                    'Phone Number': c.phone_number or '',
                    'City': c.city or '',
                    'Address': c.address or '',
                    'GSTIN': c.gst_number or '',
                    'PAN / Aadhaar': c.aadhaar_pan or '',
                    'Outstanding Balance (Rs)': _safe_float(c_bal),
                    'Gold Ledger (g)': _safe_float(c_gold),
                    'Silver Ledger (g)': _safe_float(c_silver),
                    'Total Bills Count': bill_count
                })
            if not cust_rows:
                cust_rows.append({'Customer ID': 0, 'Customer Name': 'No customers registered yet', 'Phone Number': '', 'City': '', 'Address': '', 'GSTIN': '', 'PAN / Aadhaar': '', 'Outstanding Balance (Rs)': 0, 'Gold Ledger (g)': 0, 'Silver Ledger (g)': 0, 'Total Bills Count': 0})
            pd.DataFrame(cust_rows).to_excel(writer, sheet_name='Customers', index=False)

            # 8. Customer Ledgers (Store Scoped)
            c_ledgers = db.query(CustomerLedger).filter(CustomerLedger.customer_id.in_(customer_ids)).order_by(CustomerLedger.id.desc()).all() if customer_ids else []
            c_ledg_rows = []
            for cl in c_ledgers:
                c_name = f"{cl.customer.first_name} {cl.customer.last_name or ''}".strip() if cl.customer else ""
                ledger_dt = cl.date.strftime('%Y-%m-%d %I:%M %p') if hasattr(cl, 'date') and cl.date else (cl.created_at.strftime('%Y-%m-%d %I:%M %p') if hasattr(cl, 'created_at') and cl.created_at else '')
                c_ledg_rows.append({
                    'Date': ledger_dt,
                    'Customer Name': c_name,
                    'Voucher No': cl.voucher_number or '',
                    'Voucher Type': cl.voucher_type or '',
                    'Debit (Rs)': _safe_float(cl.debit),
                    'Credit (Rs)': _safe_float(cl.credit),
                    'Cash Balance (Rs)': _safe_float(cl.balance),
                    'Gold Debit (g)': _safe_float(cl.gold_debit),
                    'Gold Credit (g)': _safe_float(cl.gold_credit),
                    'Gold Balance (g)': _safe_float(cl.gold_balance),
                    'Silver Debit (g)': _safe_float(cl.silver_debit),
                    'Silver Credit (g)': _safe_float(cl.silver_credit),
                    'Silver Balance (g)': _safe_float(cl.silver_balance),
                    'Description / Note': cl.description or ''
                })
            if not c_ledg_rows:
                c_ledg_rows.append({'Date': '', 'Customer Name': 'No customer ledger entries yet', 'Voucher No': '', 'Voucher Type': '', 'Debit (Rs)': 0, 'Credit (Rs)': 0, 'Cash Balance (Rs)': 0, 'Gold Debit (g)': 0, 'Gold Credit (g)': 0, 'Gold Balance (g)': 0, 'Silver Debit (g)': 0, 'Silver Credit (g)': 0, 'Silver Balance (g)': 0, 'Description / Note': ''})
            pd.DataFrame(c_ledg_rows).to_excel(writer, sheet_name='Customer_Ledgers', index=False)

            # 9. Suppliers (Store Scoped)
            sellers = db.query(Seller).filter(Seller.store_id == store_id).order_by(Seller.id.desc()).all()
            seller_ids = [s.id for s in sellers]
            seller_rows = []
            for s in sellers:
                s_phone = s.mobile if hasattr(s, 'mobile') else getattr(s, 'phone', '')
                s_bal = s.outstanding_balance if hasattr(s, 'outstanding_balance') else getattr(s, 'balance', 0)
                s_gold = s.fine_gold_balance if hasattr(s, 'fine_gold_balance') else getattr(s, 'gold_balance', 0)
                s_silver = s.fine_silver_balance if hasattr(s, 'fine_silver_balance') else getattr(s, 'silver_balance', 0)
                seller_rows.append({
                    'Supplier ID': s.id,
                    'Supplier Name': s.name,
                    'Phone / Mobile': s_phone or '',
                    'City': s.city or '',
                    'Address': s.address or '',
                    'GSTIN': s.gst_number or '',
                    'Outstanding Balance (Rs)': _safe_float(s_bal),
                    'Gold Balance (g)': _safe_float(s_gold),
                    'Silver Balance (g)': _safe_float(s_silver)
                })
            if not seller_rows:
                seller_rows.append({'Supplier ID': 0, 'Supplier Name': 'No suppliers registered yet', 'Phone / Mobile': '', 'City': '', 'Address': '', 'GSTIN': '', 'Outstanding Balance (Rs)': 0, 'Gold Balance (g)': 0, 'Silver Balance (g)': 0})
            pd.DataFrame(seller_rows).to_excel(writer, sheet_name='Suppliers', index=False)

            # 10. Supplier Ledgers (Store Scoped)
            s_ledgers = db.query(SupplierLedger).filter(SupplierLedger.seller_id.in_(seller_ids)).order_by(SupplierLedger.id.desc()).all() if seller_ids else []
            s_ledg_rows = []
            for sl in s_ledgers:
                s_name = sl.seller.name if sl.seller else ''
                ledger_dt = sl.date.strftime('%Y-%m-%d %I:%M %p') if hasattr(sl, 'date') and sl.date else (sl.created_at.strftime('%Y-%m-%d %I:%M %p') if hasattr(sl, 'created_at') and sl.created_at else '')
                s_ledg_rows.append({
                    'Date': ledger_dt,
                    'Supplier Name': s_name,
                    'Voucher No': sl.voucher_number or '',
                    'Voucher Type': sl.voucher_type or '',
                    'Debit (Rs)': _safe_float(sl.debit),
                    'Credit (Rs)': _safe_float(sl.credit),
                    'Cash Balance (Rs)': _safe_float(sl.balance),
                    'Gold Debit (g)': _safe_float(sl.gold_debit),
                    'Gold Credit (g)': _safe_float(sl.gold_credit),
                    'Gold Balance (g)': _safe_float(sl.gold_balance),
                    'Silver Debit (g)': _safe_float(sl.silver_debit),
                    'Silver Credit (g)': _safe_float(sl.silver_credit),
                    'Silver Balance (g)': _safe_float(sl.silver_balance),
                    'Description / Note': sl.description or ''
                })
            if not s_ledg_rows:
                s_ledg_rows.append({'Date': '', 'Supplier Name': 'No supplier ledger entries yet', 'Voucher No': '', 'Voucher Type': '', 'Debit (Rs)': 0, 'Credit (Rs)': 0, 'Cash Balance (Rs)': 0, 'Gold Debit (g)': 0, 'Gold Credit (g)': 0, 'Gold Balance (g)': 0, 'Silver Debit (g)': 0, 'Silver Credit (g)': 0, 'Silver Balance (g)': 0, 'Description / Note': ''})
            pd.DataFrame(s_ledg_rows).to_excel(writer, sheet_name='Supplier_Ledgers', index=False)

            # 11. Inventory Stock (Store Scoped)
            stock_items = db.query(StockItem).filter(StockItem.store_id == store_id).order_by(StockItem.id.desc()).all()
            inv_stock_rows = []
            for item in stock_items:
                inv_stock_rows.append({
                    'Item Code': item.item_code or f"ITM-{item.id}",
                    'Item Name': item.item_name,
                    'Metal Type': item.metal or '',
                    'Category': item.category or '',
                    'Gross Wt (g)': _safe_float(item.gross_weight),
                    'Stone Wt (g)': _safe_float(item.stone_weight),
                    'Net Wt (g)': _safe_float(item.net_weight),
                    'Making Charge': _safe_float(item.making_charge),
                    'Hallmark': _safe_float(item.hallmark),
                    'Quantity': 1,
                    'Created Date': item.created_at.strftime('%Y-%m-%d') if hasattr(item, 'created_at') and item.created_at else ''
                })
            if not inv_stock_rows:
                inv_stock_rows.append({'Item Code': 'N/A', 'Item Name': 'No stock items in this store yet', 'Metal Type': '', 'Category': '', 'Gross Wt (g)': 0, 'Stone Wt (g)': 0, 'Net Wt (g)': 0, 'Making Charge': 0, 'Hallmark': 0, 'Quantity': 0, 'Created Date': ''})
            pd.DataFrame(inv_stock_rows).to_excel(writer, sheet_name='Inventory_Stock', index=False)

            # 12. Metal Rates
            rates = db.query(MetalRate).order_by(MetalRate.id.desc()).all()
            rate_rows = []
            for r in rates:
                rate_rows.append({
                    'Metal': r.metal_type,
                    'Purity': r.purity,
                    'Rate (Rs)': _safe_float(r.rate),
                    'Unit': 'per 10g' if (r.metal_type and str(r.metal_type).lower() == 'gold') else 'per kg',
                    'Effective Date': r.effective_date.strftime('%Y-%m-%d %I:%M %p') if r.effective_date else ''
                })
            if not rate_rows:
                rate_rows.append({'Metal': 'N/A', 'Purity': '', 'Rate (Rs)': 0, 'Unit': '', 'Effective Date': ''})
            pd.DataFrame(rate_rows).to_excel(writer, sheet_name='Metal_Rates', index=False)

            # 13. Expenses (Store Scoped)
            expenses = db.query(Expense).filter(Expense.store_id == store_id).order_by(Expense.id.desc()).all()
            exp_rows = []
            for ex in expenses:
                exp_date = ex.expense_date.strftime('%Y-%m-%d') if hasattr(ex, 'expense_date') and ex.expense_date else (ex.date.strftime('%Y-%m-%d') if hasattr(ex, 'date') and ex.date else '')
                cat_str = ex.category.value if hasattr(ex.category, 'value') else _safe_str(ex.category, 'General')
                exp_rows.append({
                    'Expense ID': ex.id,
                    'Date': exp_date,
                    'Category': cat_str,
                    'Amount (Rs)': _safe_float(ex.amount),
                    'Description': ex.description or ''
                })
            if not exp_rows:
                exp_rows.append({'Expense ID': 0, 'Date': '', 'Category': 'No expenses recorded', 'Amount (Rs)': 0, 'Description': ''})
            pd.DataFrame(exp_rows).to_excel(writer, sheet_name='Expenses', index=False)

            # 14. Store Settings (Store Scoped)
            set_rows = [
                {'Setting Parameter': 'Store ID', 'Configured Value': str(store_id)},
                {'Setting Parameter': 'Store Name', 'Configured Value': store.name if store else ''},
                {'Setting Parameter': 'Phone Number', 'Configured Value': store.phone if store else ''},
                {'Setting Parameter': 'Email Address', 'Configured Value': store.email if store else ''},
                {'Setting Parameter': 'Store Address', 'Configured Value': store.address if store else ''},
                {'Setting Parameter': 'GSTIN', 'Configured Value': store.gstin if store else ''},
                {'Setting Parameter': 'PAN', 'Configured Value': store.pan if store else ''},
                {'Setting Parameter': 'Tagline', 'Configured Value': store.tagline if store else ''},
                {'Setting Parameter': 'Logo URL', 'Configured Value': store.logo_url if store else ''},
            ]
            all_s = db.query(Setting).all()
            prefix = f"store_{store_id}_"
            for s in all_s:
                if store_id == 1 and not s.key.startswith("store_"):
                    set_rows.append({'Setting Parameter': s.key.replace('_', ' ').title(), 'Configured Value': s.value})
                elif s.key.startswith(prefix):
                    clean_k = s.key[len(prefix):].replace('_', ' ').title()
                    set_rows.append({'Setting Parameter': clean_k, 'Configured Value': s.value})

            pd.DataFrame(set_rows).to_excel(writer, sheet_name='Store_Settings', index=False)

        # Apply Openpyxl Styling
        wb = openpyxl.load_workbook(excel_path)
        header_fill = PatternFill(start_color='0B132B', end_color='0B132B', fill_type='solid')
        header_font = Font(name='Segoe UI', size=11, bold=True, color='FFFFFF')
        thin_border = Border(
            left=Side(style='thin', color='E5E7EB'),
            right=Side(style='thin', color='E5E7EB'),
            top=Side(style='thin', color='E5E7EB'),
            bottom=Side(style='thin', color='E5E7EB')
        )

        for sheet in wb.worksheets:
            sheet.views.sheetView[0].showGridLines = True
            for col_idx in range(1, sheet.max_column + 1):
                cell = sheet.cell(row=1, column=col_idx)
                cell.fill = header_fill
                cell.font = header_font
                cell.alignment = Alignment(horizontal='center', vertical='center', wrap_text=False)

            for col in sheet.columns:
                max_len = 0
                col_letter = get_column_letter(col[0].column)
                for cell in col:
                    cell.border = thin_border
                    if cell.row > 1 and isinstance(cell.value, (int, float)):
                        cell.alignment = Alignment(horizontal='right')
                    val_str = str(cell.value or '')
                    if len(val_str) > max_len:
                        max_len = len(val_str)
                sheet.column_dimensions[col_letter].width = max(max_len + 4, 14)

        if wb.worksheets:
            wb.active = wb.worksheets[0]

        wb.save(excel_path)

    except Exception as e:
        if os.path.exists(excel_path):
            try:
                os.remove(excel_path)
            except Exception:
                pass
        print(f"Curated Master Excel Export failed: {e}")
        raise HTTPException(status_code=500, detail="Master Excel Export failed")
        
    return FileResponse(
        path=excel_path, 
        filename=excel_filename, 
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        background=BackgroundTask(os.remove, excel_path)
    )
