from app.db.database import engine
from sqlalchemy import text

conn = engine.connect()

# Check if item_code exists
result = conn.execute(text("SHOW COLUMNS FROM inventory LIKE 'item_code'"))
rows = result.fetchall()

if len(rows) == 0:
    # Add item_code column
    conn.execute(text("ALTER TABLE inventory ADD COLUMN item_code VARCHAR(20)"))
    conn.commit()
    print("Added item_code column")

conn.close()
