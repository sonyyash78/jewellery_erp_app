import os

for path in [
    r"C:\Users\YASH SONI\Desktop\jeweller-app\frontend\src\pages\exchange\OldItemsForm.tsx",
    r"C:\Users\YASH SONI\Desktop\jeweller-app\frontend\src\pages\purchase\PurchaseMetalForm.tsx"
]:
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            t = f.read()
        t = t.replace("dY Gold", "🟡 Gold")
        t = t.replace("dY^ Silver", "⚪ Silver")
        t = t.replace("dY'Z Diamond", "💎 Diamond")
        t = t.replace(",1", "₹")
        t = t.replace("?\"", "—")
        with open(path, "w", encoding="utf-8") as f:
            f.write(t)
        print("Cleaned", path)
