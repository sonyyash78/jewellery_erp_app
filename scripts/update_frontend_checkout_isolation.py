def update_frontend_checkouts():
    # 1. axiosClient.ts
    path_axios = r"C:\Users\YASH SONI\Desktop\jeweller-app\frontend\src\api\axiosClient.ts"
    with open(path_axios, "r", encoding="utf-8") as f:
        c_axios = f.read()
    
    old_interceptor = """// Intercept requests to attach JWT & Company ID
axiosClient.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().token;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    const companyId = localStorage.getItem('erp_company_id') || '1';
    config.headers['X-Company-ID'] = companyId;
    return config;
  },
  (error) => Promise.reject(error)
);"""

    new_interceptor = """import { useCompanyStore } from '../store/companyStore';

// Intercept requests to attach JWT & Company ID
axiosClient.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().token;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    const storeCid = useCompanyStore.getState().currentCompanyId;
    const companyId = storeCid ? String(storeCid) : (localStorage.getItem('erp_company_id') || '1');
    if (!config.headers['X-Company-ID']) {
      config.headers['X-Company-ID'] = companyId;
    }
    return config;
  },
  (error) => Promise.reject(error)
);"""

    c_axios_norm = c_axios.replace("\r\n", "\n")
    o_axios_norm = old_interceptor.replace("\r\n", "\n")
    n_axios_norm = new_interceptor.replace("\r\n", "\n")
    if o_axios_norm in c_axios_norm:
        c_axios_norm = c_axios_norm.replace(o_axios_norm, n_axios_norm)
        with open(path_axios, "w", encoding="utf-8") as f:
            f.write(c_axios_norm.replace("\n", "\r\n"))
        print("Updated axiosClient.ts request interceptor")

    # 2. CheckoutModal.tsx
    path_check = r"C:\Users\YASH SONI\Desktop\jeweller-app\frontend\src\pages\billing\CheckoutModal.tsx"
    with open(path_check, "r", encoding="utf-8") as f:
        c_check = f.read()

    target_check = """      idempotency_key: idempotencyKey,
    };"""
    replace_check = """      idempotency_key: idempotencyKey,
      company_id: currentCompanyId || 1,
    };"""
    if target_check in c_check and "company_id: currentCompanyId" not in c_check:
        c_check = c_check.replace(target_check, replace_check)
        with open(path_check, "w", encoding="utf-8") as f:
            f.write(c_check)
        print("Updated CheckoutModal.tsx company_id in finalPayload")

    # 3. PurchaseCheckoutModal.tsx
    path_pur = r"C:\Users\YASH SONI\Desktop\jeweller-app\frontend\src\pages\purchase\PurchaseCheckoutModal.tsx"
    with open(path_pur, "r", encoding="utf-8") as f:
        c_pur = f.read()

    if "useCompanyStore" not in c_pur:
        c_pur = "import { useCompanyStore } from '../../store/companyStore';\n" + c_pur
    if "const { currentCompanyId } = useCompanyStore();" not in c_pur:
        c_pur = c_pur.replace(
            "export function PurchaseCheckoutModal({",
            "export function PurchaseCheckoutModal({\n  // company hook\n"
        ).replace(
            "// company hook\n",
            ""
        )
        # Add inside component body
        c_pur = c_pur.replace(
            "export function PurchaseCheckoutModal({ items, totals, onClose, onSuccess }: PurchaseCheckoutModalProps) {",
            "export function PurchaseCheckoutModal({ items, totals, onClose, onSuccess }: PurchaseCheckoutModalProps) {\n  const { currentCompanyId } = useCompanyStore();"
        )
    
    target_pur = """      gold_balance_metal_weight: goldBalMetal,
      silver_balance_metal_weight: silverBalMetal,
    };

    try {
      const res = await axiosClient.post('/purchases/', finalPayload);"""

    replace_pur = """      gold_balance_metal_weight: goldBalMetal,
      silver_balance_metal_weight: silverBalMetal,
      company_id: currentCompanyId || 1,
    };

    try {
      const res = await axiosClient.post('/purchases/', finalPayload, {
        headers: {
          'X-Company-ID': String(currentCompanyId || 1)
        }
      });"""

    c_pur_norm = c_pur.replace("\r\n", "\n")
    t_pur_norm = target_pur.replace("\r\n", "\n")
    r_pur_norm = replace_pur.replace("\r\n", "\n")
    if t_pur_norm in c_pur_norm:
        c_pur_norm = c_pur_norm.replace(t_pur_norm, r_pur_norm)
        with open(path_pur, "w", encoding="utf-8") as f:
            f.write(c_pur_norm.replace("\n", "\r\n"))
        print("Updated PurchaseCheckoutModal.tsx company_id")

    # 4. ExchangeCheckoutModal.tsx
    path_exc = r"C:\Users\YASH SONI\Desktop\jeweller-app\frontend\src\pages\exchange\ExchangeCheckoutModal.tsx"
    with open(path_exc, "r", encoding="utf-8") as f:
        c_exc = f.read()

    if "useCompanyStore" not in c_exc:
        c_exc = "import { useCompanyStore } from '../../store/companyStore';\n" + c_exc
    if "const { currentCompanyId } = useCompanyStore();" not in c_exc:
        c_exc = c_exc.replace(
            "export function ExchangeCheckoutModal({",
            "export function ExchangeCheckoutModal({\n  // company hook\n"
        ).replace("// company hook\n", "")
        c_exc = c_exc.replace(
            "export function ExchangeCheckoutModal({ oldItems, newItems, totals, onClose, onSuccess }: ExchangeCheckoutModalProps) {",
            "export function ExchangeCheckoutModal({ oldItems, newItems, totals, onClose, onSuccess }: ExchangeCheckoutModalProps) {\n  const { currentCompanyId } = useCompanyStore();"
        )

    target_exc = """      gold_balance_metal_weight: goldBalMetal,
      silver_balance_metal_weight: silverBalMetal,
    };

    try {
      const res = await axiosClient.post('/exchanges/', finalPayload);"""

    replace_exc = """      gold_balance_metal_weight: goldBalMetal,
      silver_balance_metal_weight: silverBalMetal,
      company_id: currentCompanyId || 1,
    };

    try {
      const res = await axiosClient.post('/exchanges/', finalPayload, {
        headers: {
          'X-Company-ID': String(currentCompanyId || 1)
        }
      });"""

    c_exc_norm = c_exc.replace("\r\n", "\n")
    t_exc_norm = target_exc.replace("\r\n", "\n")
    r_exc_norm = replace_exc.replace("\r\n", "\n")
    if t_exc_norm in c_exc_norm:
        c_exc_norm = c_exc_norm.replace(t_exc_norm, r_exc_norm)
        with open(path_exc, "w", encoding="utf-8") as f:
            f.write(c_exc_norm.replace("\n", "\r\n"))
        print("Updated ExchangeCheckoutModal.tsx company_id")

if __name__ == "__main__":
    update_frontend_checkouts()
