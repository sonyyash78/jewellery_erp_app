import re

def fix_backend_services():
    # 1. Fix report_service.py get_metal_flow_report
    path_report = r"C:\Users\YASH SONI\Desktop\jeweller-app\backend\app\services\report_service.py"
    with open(path_report, "r", encoding="utf-8") as f:
        content = f.read()

    # Replace get_metal_flow_report signature
    old_sig = """    @staticmethod
    def get_metal_flow_report(
        db: Session,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        store_id: Optional[int] = None
    ) -> Dict[str, any]:"""

    new_sig = """    @staticmethod
    def get_metal_flow_report(
        db: Session,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        store_id: Optional[int] = None,
        company_id: Optional[int] = None
    ) -> Dict[str, any]:"""

    content = content.replace(old_sig, new_sig)

    # Add company filter inside get_metal_flow_report queries
    filter_inv = """        if store_id is not None:
            g_inv_q = g_inv_q.filter(Invoice.store_id == store_id)"""
    filter_inv_rep = """        if store_id is not None:
            g_inv_q = g_inv_q.filter(Invoice.store_id == store_id)
        if company_id is not None:
            g_inv_q = g_inv_q.filter(_company_filter(Invoice, company_id))"""
    if filter_inv in content and "filter(_company_filter(Invoice, company_id))" not in content:
        content = content.replace(filter_inv, filter_inv_rep)

    filter_sinv = """        if store_id is not None:
            s_inv_q = s_inv_q.filter(Invoice.store_id == store_id)"""
    filter_sinv_rep = """        if store_id is not None:
            s_inv_q = s_inv_q.filter(Invoice.store_id == store_id)
        if company_id is not None:
            s_inv_q = s_inv_q.filter(_company_filter(Invoice, company_id))"""
    if filter_sinv in content:
        content = content.replace(filter_sinv, filter_sinv_rep)

    filter_gdep = """        if store_id is not None:
            g_inv_dep_q = g_inv_dep_q.filter(Invoice.store_id == store_id)"""
    filter_gdep_rep = """        if store_id is not None:
            g_inv_dep_q = g_inv_dep_q.filter(Invoice.store_id == store_id)
        if company_id is not None:
            g_inv_dep_q = g_inv_dep_q.filter(_company_filter(Invoice, company_id))"""
    if filter_gdep in content:
        content = content.replace(filter_gdep, filter_gdep_rep)

    filter_sdep = """        if store_id is not None:
            s_inv_dep_q = s_inv_dep_q.filter(Invoice.store_id == store_id)"""
    filter_sdep_rep = """        if store_id is not None:
            s_inv_dep_q = s_inv_dep_q.filter(Invoice.store_id == store_id)
        if company_id is not None:
            s_inv_dep_q = s_inv_dep_q.filter(_company_filter(Invoice, company_id))"""
    if filter_sdep in content:
        content = content.replace(filter_sdep, filter_sdep_rep)

    filter_exc_ng = """        if store_id is not None:
            exc_new_gold_q = exc_new_gold_q.filter(Exchange.store_id == store_id)"""
    filter_exc_ng_rep = """        if store_id is not None:
            exc_new_gold_q = exc_new_gold_q.filter(Exchange.store_id == store_id)
        if company_id is not None:
            exc_new_gold_q = exc_new_gold_q.filter(_company_filter(Exchange, company_id))"""
    if filter_exc_ng in content:
        content = content.replace(filter_exc_ng, filter_exc_ng_rep)

    filter_exc_ns = """        if store_id is not None:
            exc_new_silver_q = exc_new_silver_q.filter(Exchange.store_id == store_id)"""
    filter_exc_ns_rep = """        if store_id is not None:
            exc_new_silver_q = exc_new_silver_q.filter(Exchange.store_id == store_id)
        if company_id is not None:
            exc_new_silver_q = exc_new_silver_q.filter(_company_filter(Exchange, company_id))"""
    if filter_exc_ns in content:
        content = content.replace(filter_exc_ns, filter_exc_ns_rep)

    filter_exc_og = """        if store_id is not None:
            exc_old_gold_q = exc_old_gold_q.filter(Exchange.store_id == store_id)"""
    filter_exc_og_rep = """        if store_id is not None:
            exc_old_gold_q = exc_old_gold_q.filter(Exchange.store_id == store_id)
        if company_id is not None:
            exc_old_gold_q = exc_old_gold_q.filter(_company_filter(Exchange, company_id))"""
    if filter_exc_og in content:
        content = content.replace(filter_exc_og, filter_exc_og_rep)

    filter_exc_os = """        if store_id is not None:
            exc_old_silver_q = exc_old_silver_q.filter(Exchange.store_id == store_id)"""
    filter_exc_os_rep = """        if store_id is not None:
            exc_old_silver_q = exc_old_silver_q.filter(Exchange.store_id == store_id)
        if company_id is not None:
            exc_old_silver_q = exc_old_silver_q.filter(_company_filter(Exchange, company_id))"""
    if filter_exc_os in content:
        content = content.replace(filter_exc_os, filter_exc_os_rep)

    filter_pur_g = """        if store_id is not None:
            pur_gold_q = pur_gold_q.filter(Purchase.store_id == store_id)"""
    filter_pur_g_rep = """        if store_id is not None:
            pur_gold_q = pur_gold_q.filter(Purchase.store_id == store_id)
        if company_id is not None:
            pur_gold_q = pur_gold_q.filter(_company_filter(Purchase, company_id))"""
    if filter_pur_g in content:
        content = content.replace(filter_pur_g, filter_pur_g_rep)

    filter_pur_s = """        if store_id is not None:
            pur_silver_q = pur_silver_q.filter(Purchase.store_id == store_id)"""
    filter_pur_s_rep = """        if store_id is not None:
            pur_silver_q = pur_silver_q.filter(Purchase.store_id == store_id)
        if company_id is not None:
            pur_silver_q = pur_silver_q.filter(_company_filter(Purchase, company_id))"""
    if filter_pur_s in content:
        content = content.replace(filter_pur_s, filter_pur_s_rep)

    # get_inventory_report
    old_inv_sig = """    @staticmethod
    def get_inventory_report(
        db: Session,
        store_id: Optional[int] = None
    ) -> Dict[str, any]:"""
    new_inv_sig = """    @staticmethod
    def get_inventory_report(
        db: Session,
        store_id: Optional[int] = None,
        company_id: Optional[int] = None
    ) -> Dict[str, any]:"""
    content = content.replace(old_inv_sig, new_inv_sig)

    with open(path_report, "w", encoding="utf-8") as f:
        f.write(content)
    print("Fixed report_service.py get_metal_flow_report and get_inventory_report")

def fix_purchases_api():
    path = r"C:\Users\YASH SONI\Desktop\jeweller-app\backend\app\api\v1\purchases.py"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    # Ensure target_company_id is resolved and passed to Purchase(...)
    target = """    # Create purchase record first

    db_purchase = Purchase(

        store_id=store_id,"""

    replacement = """    # Resolve target operating company
    target_company_id = None
    if x_company_id and str(x_company_id).strip().isdigit():
        target_company_id = int(str(x_company_id).strip())
    if not target_company_id and getattr(purchase_in, 'company_id', None):
        target_company_id = int(purchase_in.company_id)
    if not target_company_id:
        target_company_id = 1

    # Create purchase record first
    db_purchase = Purchase(
        store_id=store_id,
        company_id=target_company_id,"""

    if target in content:
        content = content.replace(target, replacement)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print("Fixed purchases.py create_unified_purchase company_id")
    else:
        # Check normalized
        c_norm = content.replace("\r\n", "\n")
        t_norm = target.replace("\r\n", "\n")
        r_norm = replacement.replace("\r\n", "\n")
        if t_norm in c_norm:
            c_norm = c_norm.replace(t_norm, r_norm)
            with open(path, "w", encoding="utf-8") as f:
                f.write(c_norm.replace("\n", "\r\n"))
            print("Fixed purchases.py create_unified_purchase company_id (normalized)")
        else:
            print("Notice: target in purchases.py not matched")

def fix_exchanges_api():
    path = r"C:\Users\YASH SONI\Desktop\jeweller-app\backend\app\api\v1\exchanges.py"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    target = """    # Create Exchange

    exchange = Exchange(

        store_id=store_id,"""

    replacement = """    # Resolve target operating company
    target_company_id = None
    if x_company_id and str(x_company_id).strip().isdigit():
        target_company_id = int(str(x_company_id).strip())
    if not target_company_id and getattr(exchange_in, 'company_id', None):
        target_company_id = int(exchange_in.company_id)
    if not target_company_id:
        target_company_id = 1

    # Create Exchange
    exchange = Exchange(
        store_id=store_id,
        company_id=target_company_id,"""

    if target in content:
        content = content.replace(target, replacement)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print("Fixed exchanges.py create_exchange company_id")
    else:
        c_norm = content.replace("\r\n", "\n")
        t_norm = target.replace("\r\n", "\n")
        r_norm = replacement.replace("\r\n", "\n")
        if t_norm in c_norm:
            c_norm = c_norm.replace(t_norm, r_norm)
            with open(path, "w", encoding="utf-8") as f:
                f.write(c_norm.replace("\n", "\r\n"))
            print("Fixed exchanges.py create_exchange company_id (normalized)")
        else:
            print("Notice: target in exchanges.py not matched")

def fix_invoices_api():
    path = r"C:\Users\YASH SONI\Desktop\jeweller-app\backend\app\api\v1\invoices.py"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    target = """    # Resolve target company ID from payload, header, or default to 1

    target_company_id = getattr(invoice_in, 'company_id', None)

    if not target_company_id and x_company_id and x_company_id.isdigit():

        target_company_id = int(x_company_id)

    if not target_company_id:

        target_company_id = 1"""

    # Give X-Company-ID precedence over default 1 from schema!
    replacement = """    # Resolve target company ID with X-Company-ID session priority
    target_company_id = None
    if x_company_id and str(x_company_id).strip().isdigit():
        target_company_id = int(str(x_company_id).strip())
    if not target_company_id and getattr(invoice_in, 'company_id', None):
        target_company_id = int(invoice_in.company_id)
    if not target_company_id:
        target_company_id = 1"""

    c_norm = content.replace("\r\n", "\n")
    t_norm = target.replace("\r\n", "\n")
    r_norm = replacement.replace("\r\n", "\n")
    if t_norm in c_norm:
        c_norm = c_norm.replace(t_norm, r_norm)
        with open(path, "w", encoding="utf-8") as f:
            f.write(c_norm.replace("\n", "\r\n"))
        print("Fixed invoices.py target_company_id precedence")
    else:
        print("Notice: target in invoices.py not matched")

def fix_schemas():
    path_inv = r"C:\Users\YASH SONI\Desktop\jeweller-app\backend\app\schemas\invoice.py"
    with open(path_inv, "r", encoding="utf-8") as f:
        c_inv = f.read()
    c_inv = c_inv.replace("company_id: Optional[int] = 1", "company_id: Optional[int] = None")
    with open(path_inv, "w", encoding="utf-8") as f:
        f.write(c_inv)
    print("Fixed invoice schema company_id default to None")

    path_exc = r"C:\Users\YASH SONI\Desktop\jeweller-app\backend\app\schemas\exchange.py"
    with open(path_exc, "r", encoding="utf-8") as f:
        c_exc = f.read()
    c_exc = c_exc.replace("company_id: Optional[int] = 1", "company_id: Optional[int] = None")
    with open(path_exc, "w", encoding="utf-8") as f:
        f.write(c_exc)
    print("Fixed exchange schema company_id default to None")

if __name__ == "__main__":
    fix_backend_services()
    fix_purchases_api()
    fix_exchanges_api()
    fix_invoices_api()
    fix_schemas()
