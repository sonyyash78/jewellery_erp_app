import shutil
import os

portable_root = r"C:\Users\YASH SONI\Desktop\Jewellery_ERP_Desktop_Portable\resources"
src_frontend_dist = r"C:\Users\YASH SONI\Desktop\jeweller-app\frontend\dist"
dest_frontend = os.path.join(portable_root, "frontend")

src_backend = r"C:\Users\YASH SONI\Desktop\jeweller-app\backend"
dest_backend = os.path.join(portable_root, "backend")

# 1. Sync Frontend
if os.path.exists(src_frontend_dist):
    if os.path.exists(dest_frontend):
        shutil.rmtree(dest_frontend)
    shutil.copytree(src_frontend_dist, dest_frontend)
    print("Copied frontend dist to portable resources/frontend")

# 2. Sync Backend files
files_to_sync = [
    r"app\api\v1\sellers.py",
    r"app\api\v1\customers.py",
    r"app\models\diamond_calculation.py",
    r"app\services\calculation_service.py",
    r"app\services\gst_pdf_template.py",
    r"app\services\gst_engine.py",
    r"app\services\sequence_service.py",
    r"app\services\storage_service.py"
]

for rel_path in files_to_sync:
    s = os.path.join(src_backend, rel_path)
    d = os.path.join(dest_backend, rel_path)
    if os.path.exists(s):
        os.makedirs(os.path.dirname(d), exist_ok=True)
        shutil.copy2(s, d)
        print(f"Synced {rel_path} to portable backend")

print("Portable app resources fully synced!")
