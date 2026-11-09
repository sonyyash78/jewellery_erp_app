p = r"C:\Users\YASH SONI\Desktop\jeweller-app\backend\app\api\v1\reports.py"
with open(p, "r", encoding="utf-8") as f:
    c = f.read()

c = c.replace("        store_id = require_tenant_id(current_user)", "    store_id = require_tenant_id(current_user)")

with open(p, "w", encoding="utf-8") as f:
    f.write(c)

print("Fixed indentation in reports.py")
