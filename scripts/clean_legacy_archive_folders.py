import shutil
from pathlib import Path

arch_dir = Path(r"C:\Users\YASH SONI\JewelleryERP_Data\Archived_PDFs")
for item in arch_dir.iterdir():
    if item.is_dir() and item.name not in ["GST", "Without_GST"]:
        print(f"Removing legacy unpartitioned folder: {item.name}")
        shutil.rmtree(item, ignore_errors=True)

print("Remaining in Archived_PDFs:", [p.name for p in arch_dir.iterdir() if p.is_dir()])
