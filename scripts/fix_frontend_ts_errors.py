import os

# 1. LiveBillSummary.tsx
p_live = r"C:\Users\YASH SONI\Desktop\jeweller-app\frontend\src\pages\billing\LiveBillSummary.tsx"
with open(p_live, "r", encoding="utf-8") as f:
    c = f.read()
c = c.replace("const { currentCompanyId, currentCompany } = useCompanyStore();", "const { currentCompanyId } = useCompanyStore();")
with open(p_live, "w", encoding="utf-8") as f:
    f.write(c)
print("Fixed LiveBillSummary.tsx")

# 2. InvoiceHistory.tsx
p_inv = r"C:\Users\YASH SONI\Desktop\jeweller-app\frontend\src\pages\invoices\InvoiceHistory.tsx"
with open(p_inv, "r", encoding="utf-8") as f:
    c = f.read()
c = c.replace("const { currentCompanyId, currentCompany } = useCompanyStore();", "const { currentCompanyId } = useCompanyStore();")
with open(p_inv, "w", encoding="utf-8") as f:
    f.write(c)
print("Fixed InvoiceHistory.tsx")

# 3. ExchangeCheckoutModal.tsx
p_ex = r"C:\Users\YASH SONI\Desktop\jeweller-app\frontend\src\pages\exchange\ExchangeCheckoutModal.tsx"
with open(p_ex, "r", encoding="utf-8") as f:
    c = f.read()
if "import { useCompanyStore } from '../../store/companyStore';" not in c:
    c = "import { useCompanyStore } from '../../store/companyStore';\n" + c
c = c.replace(
    "const [loading, setLoading] = useState(false);",
    "const { currentCompanyId } = useCompanyStore();\n  const [loading, setLoading] = useState(false);"
)
with open(p_ex, "w", encoding="utf-8") as f:
    f.write(c)
print("Fixed ExchangeCheckoutModal.tsx")

# 4. PurchaseCheckoutModal.tsx
p_pur = r"C:\Users\YASH SONI\Desktop\jeweller-app\frontend\src\pages\purchase\PurchaseCheckoutModal.tsx"
with open(p_pur, "r", encoding="utf-8") as f:
    c = f.read()
if "import { useCompanyStore } from '../../store/companyStore';" not in c:
    c = "import { useCompanyStore } from '../../store/companyStore';\n" + c
c = c.replace(
    "const [loading, setLoading] = useState(false);",
    "const { currentCompanyId } = useCompanyStore();\n  const [loading, setLoading] = useState(false);"
)
with open(p_pur, "w", encoding="utf-8") as f:
    f.write(c)
print("Fixed PurchaseCheckoutModal.tsx")
