from app.db.database import engine
from sqlalchemy import text

def run_migration():
    print("Connecting to mobile database...")
    with engine.connect() as conn:
        # 1. Create stores table if not exists
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS stores (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(150) NOT NULL DEFAULT 'My Jewellery Store',
                tagline VARCHAR(255),
                owner_id INT,
                phone VARCHAR(50),
                email VARCHAR(100),
                address TEXT,
                city VARCHAR(100),
                state VARCHAR(100),
                pincode VARCHAR(20),
                gstin VARCHAR(50),
                pan VARCHAR(50),
                logo_url VARCHAR(255),
                is_active BOOLEAN DEFAULT TRUE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
        """))
        
        # 2. Insert default Saideep Jewellers store
        conn.execute(text("""
            INSERT IGNORE INTO stores (id, name, tagline, phone, email, address, gstin, is_active)
            VALUES (1, 'Saideep Jewellers', 'Premium Gold & Silver Jewellery', '9876543210', 'admin@saideep.com', 'Shop 101, Main Jewellers Market', '27AAAAA0000A1Z5', 1);
        """))
        
        # 3. Add tenant_id / store_id to tables
        tables_to_scope = [
            ('users', 'tenant_id', 'INT NULL DEFAULT 1'),
            ('invoices', 'store_id', 'INT NULL DEFAULT 1'),
            ('bills', 'store_id', 'INT NULL DEFAULT 1'),
            ('customers', 'store_id', 'INT NULL DEFAULT 1'),
            ('suppliers', 'store_id', 'INT NULL DEFAULT 1'),
            ('stock_items', 'store_id', 'INT NULL DEFAULT 1'),
            ('inventory', 'store_id', 'INT NULL DEFAULT 1'),
            ('purchases', 'store_id', 'INT NULL DEFAULT 1'),
            ('expenses', 'store_id', 'INT NULL DEFAULT 1'),
            ('exchanges', 'store_id', 'INT NULL DEFAULT 1'),
            ('metal_rates', 'store_id', 'INT NULL DEFAULT 1'),
            ('categories', 'store_id', 'INT NULL DEFAULT 1')
        ]
        
        for table, col, col_def in tables_to_scope:
            try:
                res = conn.execute(text(f"""
                    SELECT count(*) FROM information_schema.COLUMNS 
                    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = '{table}' AND COLUMN_NAME = '{col}';
                """)).scalar()
                if res == 0:
                    conn.execute(text(f"ALTER TABLE {table} ADD COLUMN {col} {col_def};"))
                    print(f"Added {col} to {table}")
                else:
                    print(f"{col} already exists in {table}")
                
                # Backfill
                conn.execute(text(f"UPDATE {table} SET {col} = 1 WHERE {col} IS NULL;"))
            except Exception as e:
                print(f"Note on {table}.{col}:", e)

        # 4. Modify indexes on customers/suppliers
        for idx_name, tbl in [('phone_number', 'customers'), ('email', 'customers'), ('mobile', 'suppliers'), ('email', 'suppliers')]:
            try:
                indexes = conn.execute(text(f"SHOW INDEX FROM {tbl} WHERE Column_name = '{idx_name}' AND Non_unique = 0;")).fetchall()
                for row in indexes:
                    key_name = row[2]
                    if key_name != 'PRIMARY':
                        conn.execute(text(f"ALTER TABLE {tbl} DROP INDEX {key_name};"))
                        print(f"Dropped unique index {key_name} on {tbl}.{idx_name}")
            except Exception as e:
                print(f"Index note on {tbl}.{idx_name}:", e)

        conn.commit()
        print("Mobile Database Migration to Multi-Tenant -> SUCCESSFUL")

if __name__ == "__main__":
    run_migration()
