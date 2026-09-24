from app.models.inventory import Inventory
from app.db.database import engine
from sqlalchemy import text

with engine.connect() as conn:
    result = conn.execute(text("SELECT column_name FROM information_schema.columns WHERE table_name = \"inventory\" AND column_name = \"item_code\""))
    rows = result.fetchall()
    if len(rows) == 0:
        conn.execute(text("ALTER TABLE inventory ADD COLUMN item_code VARCHAR(20) UNIQUE"))
        print("Added item_code column")
    else:
        print("item_code column already exists")
