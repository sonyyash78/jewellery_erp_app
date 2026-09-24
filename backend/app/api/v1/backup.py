from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
import os
import subprocess
from datetime import datetime
from app.core.config import settings

router = APIRouter()

@router.get("/download")
def download_backup():
    backup_dir = os.path.join(os.path.dirname(__file__), "..", "..", "backups")
    os.makedirs(backup_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"jewellery_erp_backup_{timestamp}.sql"
    backup_path = os.path.join(backup_dir, backup_filename)
    
    # Parse DATABASE_URL: mysql+pymysql://root:password@localhost:3306/jewellery_erp
    db_url = settings.DATABASE_URL
    if not db_url.startswith("mysql"):
        raise HTTPException(status_code=500, detail="Only MySQL is supported for backup")
        
    try:
        # Extract credentials
        auth_part = db_url.split("://")[1].split("@")[0]
        host_part = db_url.split("@")[1].split("/")[0]
        db_name = db_url.split("/")[-1].split("?")[0]
        
        user = auth_part.split(":")[0]
        password = auth_part.split(":")[1] if ":" in auth_part else ""
        
        # Decode password if URL encoded (e.g., %40 -> @)
        import urllib.parse
        password = urllib.parse.unquote(password)
        
        host = host_part.split(":")[0]
        
        # Standard mysqldump path on Windows or use from PATH
        mysqldump_path = r"C:\Program Files\MySQL\MySQL Server 8.0\bin\mysqldump.exe"
        if not os.path.exists(mysqldump_path):
            mysqldump_path = "mysqldump" # fallback to PATH
            
        cmd = [
            mysqldump_path,
            f"--user={user}",
            f"--password={password}",
            f"--host={host}",
            db_name
        ]
        
        with open(backup_path, "w", encoding="utf-8") as f:
            subprocess.run(cmd, stdout=f, check=True)
            
    except Exception as e:
        print(f"Backup failed: {e}")
        raise HTTPException(status_code=500, detail=f"Backup failed: {str(e)}")
    
    return FileResponse(
        path=backup_path, 
        filename=backup_filename, 
        media_type='application/sql'
    )

@router.get("/excel-download")
def download_excel_backup():
    import pandas as pd
    import zipfile
    from sqlalchemy import inspect
    from app.db.database import engine
    
    backup_dir = os.path.join(os.path.dirname(__file__), "..", "..", "backups")
    os.makedirs(backup_dir, exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    excel_filename = f"jewellery_erp_data_{timestamp}.xlsx"
    zip_filename = f"jewellery_erp_backup_{timestamp}.zip"
    
    excel_path = os.path.join(backup_dir, excel_filename)
    zip_path = os.path.join(backup_dir, zip_filename)
    
    try:
        # Get all table names
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        if not tables:
            raise HTTPException(status_code=404, detail="No tables found in database")
            
        # Zip multiple Excel files
        excel_paths = []
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for table in tables:
                df = pd.read_sql_table(table, engine)
                
                # Skip empty tables
                if df.empty:
                    continue
                    
                # --- SMART ENRICHMENT ---
                # Automatically add Customer Name to tables that have customer_id
                if 'customer_id' in df.columns and table != 'customers':
                    try:
                        customers_df = pd.read_sql_table('customers', engine)
                        if not customers_df.empty and 'id' in customers_df.columns and 'first_name' in customers_df.columns:
                            # Create a combined name column
                            customers_df['customer_name_calc'] = customers_df['first_name']
                            if 'last_name' in customers_df.columns:
                                customers_df['customer_name_calc'] += ' ' + customers_df['last_name'].fillna('')
                                
                            df = df.merge(customers_df[['id', 'customer_name_calc']], left_on='customer_id', right_on='id', how='left')
                            df.rename(columns={'customer_name_calc': 'customer_name'}, inplace=True)
                            if 'id_y' in df.columns: df.drop(columns=['id_y'], inplace=True)
                            if 'id_x' in df.columns: df.rename(columns={'id_x': 'id'}, inplace=True)
                            
                            # Move customer_name right next to customer_id
                            cols = df.columns.tolist()
                            c_idx = cols.index('customer_id')
                            name_col = cols.pop(cols.index('customer_name'))
                            cols.insert(c_idx + 1, name_col)
                            df = df[cols]
                    except Exception as e:
                        print("Customer merge error:", e)
                
                # Automatically add Supplier Name to tables that have seller_id
                if 'seller_id' in df.columns and table != 'sellers':
                    try:
                        sellers_df = pd.read_sql_table('sellers', engine)
                        if not sellers_df.empty and 'id' in sellers_df.columns and 'name' in sellers_df.columns:
                            df = df.merge(sellers_df[['id', 'name']], left_on='seller_id', right_on='id', how='left')
                            df.rename(columns={'name': 'supplier_name'}, inplace=True)
                            if 'id_y' in df.columns: df.drop(columns=['id_y'], inplace=True)
                            if 'id_x' in df.columns: df.rename(columns={'id_x': 'id'}, inplace=True)
                            
                            cols = df.columns.tolist()
                            c_idx = cols.index('seller_id')
                            name_col = cols.pop(cols.index('supplier_name'))
                            cols.insert(c_idx + 1, name_col)
                            df = df[cols]
                    except Exception as e:
                        print("Seller merge error:", e)
                # ------------------------
                
                # Sort descending by ID or Date so latest is at the top
                if 'id' in df.columns:
                    df.sort_values('id', ascending=False, inplace=True)
                elif 'created_at' in df.columns:
                    df.sort_values('created_at', ascending=False, inplace=True)
                elif 'date' in df.columns:
                    df.sort_values('date', ascending=False, inplace=True)
                    
                # Convert datetime columns from UTC to IST
                for col in df.select_dtypes(include=['datetime64[ns, UTC]', 'datetime64[ns]']).columns:
                    try:
                        if df[col].dt.tz is None:
                            df[col] = df[col].dt.tz_localize('UTC').dt.tz_convert('Asia/Kolkata')
                        else:
                            df[col] = df[col].dt.tz_convert('Asia/Kolkata')
                        # Format cleanly for Excel
                        df[col] = df[col].dt.strftime('%Y-%m-%d %I:%M:%S %p')
                    except Exception as e:
                        print(f"Timezone conversion error for {col}:", e)
                        
                table_excel_filename = f"{table}.xlsx"
                table_excel_path = os.path.join(backup_dir, table_excel_filename)
                
                # Write individual table to its own excel file
                df.to_excel(table_excel_path, index=False)
                excel_paths.append(table_excel_path)
                
                # Add it to zip
                zipf.write(table_excel_path, arcname=table_excel_filename)
                
        # If no tables had data, create a dummy file so zip is not empty
        if not excel_paths:
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                zipf.writestr("empty_database.txt", "No data found in any tables.")
                
        # Clean up the individual excel files
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

