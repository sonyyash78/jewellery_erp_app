import os
import shutil
import subprocess
import sys

def main():
    root = r"c:\Users\YASH SONI\Desktop\jeweller-app"
    portable = r"c:\Users\YASH SONI\Desktop\Jewellery_ERP_Desktop_Portable"
    res = os.path.join(portable, "resources")
    
    print("[1/5] Syncing Frontend to Portable resources...")
    frontend_dist = os.path.join(root, "frontend", "dist")
    target_frontend_1 = os.path.join(res, "frontend")
    target_frontend_2 = os.path.join(res, "frontend", "dist")
    
    os.makedirs(target_frontend_1, exist_ok=True)
    os.makedirs(target_frontend_2, exist_ok=True)
    
    shutil.copytree(frontend_dist, target_frontend_1, dirs_exist_ok=True)
    shutil.copytree(frontend_dist, target_frontend_2, dirs_exist_ok=True)
    print("Frontend synced to both resources/frontend and resources/frontend/dist")

    print("[2/5] Syncing Backend to Portable resources...")
    backend_src = os.path.join(root, "backend")
    backend_dst = os.path.join(res, "backend")
    os.makedirs(backend_dst, exist_ok=True)
    
    ignore_patterns = shutil.ignore_patterns(
        "venv", ".venv", "env", ".git", "__pycache__", "*.pyc", "*.db", "backups", ".env*"
    )
    
    shutil.copytree(backend_src, backend_dst, dirs_exist_ok=True, ignore=ignore_patterns)
    print("Backend synced cleanly to resources/backend")

    print("[3/5] Packing clean app.asar...")
    temp_asar_dir = os.path.join(root, "desktop", "temp_asar_build")
    if os.path.exists(temp_asar_dir):
        shutil.rmtree(temp_asar_dir, ignore_errors=True)
    os.makedirs(os.path.join(temp_asar_dir, "src", "assets"), exist_ok=True)
    
    # Copy desktop package.json
    shutil.copy2(os.path.join(root, "desktop", "package.json"), os.path.join(temp_asar_dir, "package.json"))
    # Copy src/main.js and src/preload.js
    shutil.copy2(os.path.join(root, "desktop", "src", "main.js"), os.path.join(temp_asar_dir, "src", "main.js"))
    shutil.copy2(os.path.join(root, "desktop", "src", "preload.js"), os.path.join(temp_asar_dir, "src", "preload.js"))
    # Copy assets
    for a in os.listdir(os.path.join(root, "desktop", "src", "assets")):
        shutil.copy2(os.path.join(root, "desktop", "src", "assets", a), os.path.join(temp_asar_dir, "src", "assets", a))
        
    target_asar = os.path.join(res, "app.asar")
    cmd = f'npx asar pack "{temp_asar_dir}" "{target_asar}"'
    print(f"Running: {cmd}")
    res_code = subprocess.run(cmd, shell=True)
    if res_code.returncode != 0:
        print("ERROR packing asar")
        sys.exit(1)
        
    shutil.rmtree(temp_asar_dir, ignore_errors=True)
    print(f"app.asar created successfully ({os.path.getsize(target_asar):,} bytes)")

    print("[4/5] Removing stray files in resources...")
    stray_main = os.path.join(res, "main.js")
    if os.path.exists(stray_main):
        try:
            os.remove(stray_main)
            print("Removed stray resources/main.js")
        except Exception as e:
            print("Notice:", e)

    print("[5/5] Verification...")
    print(f"- app.asar: {os.path.exists(target_asar)} ({os.path.getsize(target_asar):,} bytes)")
    print(f"- resources/frontend/index.html: {os.path.exists(os.path.join(target_frontend_1, 'index.html'))}")
    print(f"- resources/frontend/dist/index.html: {os.path.exists(os.path.join(target_frontend_2, 'index.html'))}")
    print(f"- resources/backend/run_server.py: {os.path.exists(os.path.join(backend_dst, 'run_server.py'))}")
    print("DONE: Portable distribution is fully synchronized and ready!")

if __name__ == "__main__":
    main()
