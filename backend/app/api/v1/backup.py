from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
import os
from datetime import datetime
from sqlalchemy.orm import Session
from app.core.config import settings
from app.api.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.store import Store

router = APIRouter()

def _get_tenant_queries(store_id: int):
    return {
        'invoices': f"SELECT * FROM invoices WHERE store_id = {store_id}",
        'invoice_items': f"SELECT * FROM invoice_items WHERE invoice_id IN (SELECT id FROM invoices WHERE store_id = {store_id})",
        'gold_calculations': f"SELECT * FROM gold_calculations WHERE invoice_item_id IN (SELECT id FROM invoice_items WHERE invoice_id IN (SELECT id FROM invoices WHERE store_id = {store_id}))",
        'silver_calculations': f"SELECT * FROM silver_calculations WHERE invoice_item_id IN (SELECT id FROM invoice_items WHERE invoice_id IN (SELECT id FROM invoices WHERE store_id = {store_id}))",
        'purchases': f"SELECT * FROM purchases WHERE store_id = {store_id}",
        'purchase_items': f"SELECT * FROM purchase_items WHERE purchase_id IN (SELECT id FROM purchases WHERE store_id = {store_id})",
        'exchanges': f"SELECT * FROM exchanges WHERE store_id = {store_id}",
        'exchange_items': f"SELECT * FROM exchange_items WHERE exchange_id IN (SELECT id FROM exchanges WHERE store_id = {store_id})",
        'exchange_new_items': f"SELECT * FROM exchange_new_items WHERE exchange_id IN (SELECT id FROM exchanges WHERE store_id = {store_id})",
        'customers': f"SELECT * FROM customers WHERE store_id = {store_id}",
        'customer_ledgers': f"SELECT * FROM customer_ledgers WHERE customer_id IN (SELECT id FROM customers WHERE store_id = {store_id})",
        'customer_addresses': f"SELECT * FROM customer_addresses WHERE customer_id IN (SELECT id FROM customers WHERE store_id = {store_id})",
        'sellers': f"SELECT * FROM sellers WHERE store_id = {store_id}",
        'supplier_ledgers': f"SELECT * FROM supplier_ledgers WHERE seller_id IN (SELECT id FROM sellers WHERE store_id = {store_id})",
        'suppliers': f"SELECT * FROM suppliers WHERE store_id = {store_id}",
        'stock_items': f"SELECT * FROM stock_items WHERE store_id = {store_id}",
        'expenses': f"SELECT * FROM expenses WHERE store_id = {store_id}",
        'bills': f"SELECT * FROM bills WHERE store_id = {store_id}",
        'bill_items': f"SELECT * FROM bill_items WHERE bill_id IN (SELECT id FROM bills WHERE store_id = {store_id})",
        'payments': f"SELECT * FROM payments WHERE store_id = {store_id}",
        'categories': f"SELECT * FROM categories WHERE store_id = {store_id}",
        'stores': f"SELECT * FROM stores WHERE id = {store_id}",
        'users': f"SELECT id, username, email, full_name, is_active, role_id, tenant_id FROM users WHERE tenant_id = {store_id}",
        'settings': f"SELECT * FROM settings WHERE `key` LIKE 'store_{store_id}_%%'" if store_id != 1 else "SELECT * FROM settings WHERE `key` NOT LIKE 'store_%%'",
        'metal_rates': "SELECT * FROM metal_rates"
    }

@router.get("/download")
def download_backup(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate isolated SQL backup for the current tenant's store."""
    import pandas as pd
    from app.db.database import engine

    store_id = current_user.tenant_id or 1
    store = db.query(Store).filter(Store.id == store_id).first()
    store_slug = (store.name if store else f"store_{store_id}").replace(" ", "_").lower()

    backup_dir = os.path.join(os.path.dirname(__file__), "..", "..", "backups")
    os.makedirs(backup_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"{store_slug}_backup_{timestamp}.sql"
    backup_path = os.path.join(backup_dir, backup_filename)
    
    try:
        tenant_queries = _get_tenant_queries(store_id)
        with open(backup_path, "w", encoding="utf-8") as f:
            f.write(f"-- ==========================================================\n")
            f.write(f"-- JEWELLERY APP STORE BACKUP\n")
            f.write(f"-- Store ID: {store_id}\n")
            f.write(f"-- Store Name: {store.name if store else 'Unknown'}\n")
            f.write(f"-- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"-- ==========================================================\n\n")
            f.write("SET FOREIGN_KEY_CHECKS=0;\n\n")

            for table_name, q in tenant_queries.items():
                try:
                    df = pd.read_sql_query(q, engine)
                    if df.empty:
                        continue
                    f.write(f"-- ----------------------------------------------------------\n")
                    f.write(f"-- Table: {table_name} ({len(df)} rows)\n")
                    f.write(f"-- ----------------------------------------------------------\n")
                    cols = [f"`{c}`" for c in df.columns]
                    col_str = ", ".join(cols)
                    
                    for _, row in df.iterrows():
                        vals = []
                        for val in row:
                            if pd.isna(val) or val is None:
                                vals.append("NULL")
                            elif isinstance(val, (int, float)):
                                vals.append(str(val))
                            else:
                                escaped = str(val).replace("'", "''").replace("\\", "\\\\")
                                vals.append(f"'{escaped}'")
                        f.write(f"INSERT INTO `{table_name}` ({col_str}) VALUES ({', '.join(vals)});\n")
                    f.write("\n")
                except Exception as tbl_err:
                    print(f"Skipping table {table_name} in SQL backup: {tbl_err}")

            f.write("SET FOREIGN_KEY_CHECKS=1;\n")

    except Exception as e:
        print(f"Backup failed: {e}")
        raise HTTPException(status_code=500, detail=f"Backup failed: {str(e)}")
    
    return FileResponse(
        path=backup_path, 
        filename=backup_filename, 
        media_type='application/sql'
    )

@router.get("/excel-download")
def download_excel_backup(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Download ZIP of Excel files scoped exclusively to the current tenant."""
    import pandas as pd
    import zipfile
    from app.db.database import engine
    
    store_id = current_user.tenant_id or 1
    store = db.query(Store).filter(Store.id == store_id).first()
    store_slug = (store.name if store else f"store_{store_id}").replace(" ", "_").lower()

    backup_dir = os.path.join(os.path.dirname(__file__), "..", "..", "backups")
    os.makedirs(backup_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    zip_filename = f"{store_slug}_backup_{timestamp}.zip"
    zip_path = os.path.join(backup_dir, zip_filename)
    
    try:
        tenant_queries = _get_tenant_queries(store_id)
        excel_paths = []
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for table_name, q in tenant_queries.items():
                try:
                    df = pd.read_sql_query(q, engine)
                    if df.empty:
                        continue
                    
                    for col in df.select_dtypes(include=['datetime64[ns, UTC]', 'datetime64[ns]']).columns:
                        try:
                            if df[col].dt.tz is None:
                                df[col] = df[col].dt.tz_localize('UTC').dt.tz_convert('Asia/Kolkata')
                            else:
                                df[col] = df[col].dt.tz_convert('Asia/Kolkata')
                            df[col] = df[col].dt.strftime('%Y-%m-%d %I:%M:%S %p')
                        except Exception:
                            pass

                    table_excel_filename = f"{table_name}.xlsx"
                    table_excel_path = os.path.join(backup_dir, table_excel_filename)
                    df.to_excel(table_excel_path, index=False)
                    excel_paths.append(table_excel_path)
                    zipf.write(table_excel_path, arcname=table_excel_filename)
                except Exception as t_err:
                    print(f"Error exporting table {table_name}: {t_err}")
                
        if not excel_paths:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.writestr("empty_store.txt", f"No records found for store {store_id}.")
                
        for path in excel_paths:
            if os.path.exists(path):
                os.remove(path)
            
    except Exception as e:
        print(f"Excel Backup failed: {e}")
        raise HTTPException(status_code=500, detail=f"Excel Backup failed: {str(e)}")
    
    return FileResponse(
        path=zip_path, 
        filename=zip_filename, 
        media_type='application/zip'
    )
