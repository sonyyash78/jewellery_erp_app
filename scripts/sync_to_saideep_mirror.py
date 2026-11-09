import os
import shutil

src = r"C:\Users\YASH SONI\Desktop\jeweller-app"
dst = r"C:\Users\YASH SONI\Desktop\Saideep\jewellery-erp"

ignore = shutil.ignore_patterns("node_modules", ".git", "venv", ".venv", "__pycache__", "*.pyc", "temp_asar_build", "temp_extracted_asar", "*.log")

for item in ["backend", "frontend", "desktop"]:
    s_item = os.path.join(src, item)
    d_item = os.path.join(dst, item)
    if os.path.exists(s_item):
        shutil.copytree(s_item, d_item, dirs_exist_ok=True, ignore=ignore)
        print(f"Mirrored {item} to Saideep/jewellery-erp")

print("Saideep mirror repository synced!")
