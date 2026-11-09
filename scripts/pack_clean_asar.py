import os
import shutil
import subprocess

staging = r"C:\Users\YASH SONI\Desktop\jeweller-app\desktop_staging"
dest_asar = r"C:\Users\YASH SONI\Desktop\Jewellery_ERP_Desktop_Portable\resources\app.asar"

if os.path.exists(staging):
    shutil.rmtree(staging)
os.makedirs(staging, exist_ok=True)

# Copy package.json
shutil.copy2(r"C:\Users\YASH SONI\Desktop\jeweller-app\desktop\package.json", staging)

# Copy src
shutil.copytree(r"C:\Users\YASH SONI\Desktop\jeweller-app\desktop\src", os.path.join(staging, "src"))

print(f"Staged files in {staging}")

# Pack with asar
cmd = f'npx --yes asar pack "{staging}" "{dest_asar}"'
res = subprocess.run(cmd, shell=True, capture_output=True, text=True)
print("ASAR pack returncode:", res.returncode)
print(res.stdout)
if res.stderr:
    print("Stderr:", res.stderr)

# Clean staging
shutil.rmtree(staging)
size = os.path.getsize(dest_asar)
print(f"Packed clean app.asar! Size: {size} bytes")
