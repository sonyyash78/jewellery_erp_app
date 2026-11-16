import os
import sys
from pathlib import Path

# Add backend directory to path
sys.path.append(r"c:\Users\YASH SONI\Desktop\jeweller-app\backend")

from app.db.database import SessionLocal
from app.services.pdf_archive_service import archive_all_store_documents
from app.core.config import DATA_DIR

db = SessionLocal()
try:
    print(f"Running archive_all_store_documents on {DATA_DIR}...")
    res = archive_all_store_documents(db=db, store_id=1, base_dir=DATA_DIR, force_refresh=True)
    print("Archive result:", res)
finally:
    db.close()

# List generated structure in Archived_PDFs
arch_dir = DATA_DIR / "Archived_PDFs"
print("\nGenerated Archived_PDFs folders:")
if arch_dir.exists():
    for root, dirs, files in os.walk(arch_dir):
        rel = os.path.relpath(root, arch_dir)
        if files:
            print(f"[{rel}] -> {len(files)} files: {files}")
