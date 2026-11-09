import os

p_pur = r"C:\Users\YASH SONI\Desktop\jeweller-app\frontend\src\pages\purchase\PurchaseCheckoutModal.tsx"
with open(p_pur, "r", encoding="utf-8") as f:
    c = f.read()

if "useCompanyStore" not in c:
    c = c.replace(
        "import { usePurchaseStore } from '../../store/purchaseStore';",
        "import { usePurchaseStore } from '../../store/purchaseStore';\nimport { useCompanyStore } from '../../store/companyStore';"
    )
    c = c.replace(
        "const { items, clearCart } = usePurchaseStore();",
        "const { items, clearCart } = usePurchaseStore();\n  const { currentCompanyId } = useCompanyStore();"
    )
    c = c.replace(
        "const finalPayload = {",
        "const finalPayload = {\n        company_id: currentCompanyId || 1,"
    )
    with open(p_pur, "w", encoding="utf-8") as f:
        f.write(c)
    print("Updated PurchaseCheckoutModal with company_id")
else:
    print("PurchaseCheckoutModal already has useCompanyStore")

p_ex = r"C:\Users\YASH SONI\Desktop\jeweller-app\frontend\src\pages\exchange\ExchangeCheckoutModal.tsx"
with open(p_ex, "r", encoding="utf-8") as f:
    c = f.read()

if "useCompanyStore" not in c:
    c = c.replace(
        "import { useExchangeStore } from '../../store/exchangeStore';",
        "import { useExchangeStore } from '../../store/exchangeStore';\nimport { useCompanyStore } from '../../store/companyStore';"
    )
    c = c.replace(
        "const { oldItems, newItems, clearExchange } = useExchangeStore();",
        "const { oldItems, newItems, clearExchange } = useExchangeStore();\n  const { currentCompanyId } = useCompanyStore();"
    )
    c = c.replace(
        "const finalPayload = {",
        "const finalPayload = {\n        company_id: currentCompanyId || 1,"
    )
    with open(p_ex, "w", encoding="utf-8") as f:
        f.write(c)
    print("Updated ExchangeCheckoutModal with company_id")
else:
    print("ExchangeCheckoutModal already has useCompanyStore")
