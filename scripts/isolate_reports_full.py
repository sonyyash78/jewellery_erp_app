import os
import re

# 1. Update report_service.py
p_rep_svc = r"C:\Users\YASH SONI\Desktop\jeweller-app\backend\app\services\report_service.py"
with open(p_rep_svc, "r", encoding="utf-8") as f:
    text = f.read()

# Add or_ import if not present
if "from sqlalchemy import func, and_, or_" not in text:
    text = text.replace("from sqlalchemy import func, and_", "from sqlalchemy import func, and_, or_")

# Add _company_filter helper if not present
if "def _company_filter(" not in text:
    helper = """def _company_filter(model, company_id: Optional[int]):
    if company_id is None:
        return True
    if company_id == 1:
        return or_(model.company_id == 1, model.company_id.is_(None))
    return model.company_id == company_id

"""
    text = text.replace("def _dt_range(", helper + "def _dt_range(")

# Add company_id parameter to get_sales_report
text = re.sub(
    r"def get_sales_report\(\s*db:\s*Session,\s*start_date:\s*Optional\[date\]\s*=\s*None,\s*end_date:\s*Optional\[date\]\s*=\s*None,\s*store_id:\s*Optional\[int\]\s*=\s*None\s*\)",
    "def get_sales_report(\n        db: Session,\n        start_date: Optional[date] = None,\n        end_date: Optional[date] = None,\n        store_id: Optional[int] = None,\n        company_id: Optional[int] = None\n    )",
    text
)

# Apply company filter in get_sales_report
if "inv_q = inv_q.filter(_company_filter(Invoice, company_id))" not in text:
    target_sales_filter = "if store_id is not None:\n            inv_q = inv_q.filter(Invoice.store_id == store_id)"
    repl_sales_filter = target_sales_filter + "\n        inv_q = inv_q.filter(_company_filter(Invoice, company_id))"
    text = text.replace(target_sales_filter, repl_sales_filter, 1)

    target_exc_filter = "if store_id is not None:\n            exchange_query = exchange_query.filter(Exchange.store_id == store_id)"
    repl_exc_filter = target_exc_filter + "\n        exchange_query = exchange_query.filter(_company_filter(Exchange, company_id))"
    text = text.replace(target_exc_filter, repl_exc_filter, 1)

# Add company_id to get_purchase_report
text = re.sub(
    r"def get_purchase_report\(\s*db:\s*Session,\s*start_date:\s*Optional\[date\]\s*=\s*None,\s*end_date:\s*Optional\[date\]\s*=\s*None,\s*store_id:\s*Optional\[int\]\s*=\s*None\s*\)",
    "def get_purchase_report(\n        db: Session,\n        start_date: Optional[date] = None,\n        end_date: Optional[date] = None,\n        store_id: Optional[int] = None,\n        company_id: Optional[int] = None\n    )",
    text
)

# Apply company filter in get_purchase_report
if "pur_q = pur_q.filter(_company_filter(Purchase, company_id))" not in text:
    target_pur_filter = "if store_id is not None:\n            pur_q = pur_q.filter(Purchase.store_id == store_id)"
    repl_pur_filter = target_pur_filter + "\n        pur_q = pur_q.filter(_company_filter(Purchase, company_id))"
    text = text.replace(target_pur_filter, repl_pur_filter, 1)

    # Note: the second exchange_query in get_purchase_report
    pos = text.find("exc_purchases, exc_count = exchange_query.first()")
    if pos != -1:
        idx = text.rfind("if store_id is not None:\n            exchange_query = exchange_query.filter(Exchange.store_id == store_id)", 0, pos)
        if idx != -1:
            orig = "if store_id is not None:\n            exchange_query = exchange_query.filter(Exchange.store_id == store_id)"
            text = text[:idx] + orig + "\n        exchange_query = exchange_query.filter(_company_filter(Exchange, company_id))" + text[idx+len(orig):]

# Add company_id to get_gst_report
text = re.sub(
    r"def get_gst_report\(\s*db:\s*Session,\s*start_date:\s*Optional\[date\]\s*=\s*None,\s*end_date:\s*Optional\[date\]\s*=\s*None,\s*store_id:\s*Optional\[int\]\s*=\s*None\s*\)",
    "def get_gst_report(\n        db: Session,\n        start_date: Optional[date] = None,\n        end_date: Optional[date] = None,\n        store_id: Optional[int] = None,\n        company_id: Optional[int] = None\n    )",
    text
)
text = text.replace(
    "sales_report = ReportService.get_sales_report(db, start_date, end_date, store_id=store_id)",
    "sales_report = ReportService.get_sales_report(db, start_date, end_date, store_id=store_id, company_id=company_id)"
)
text = text.replace(
    "purchase_report = ReportService.get_purchase_report(db, start_date, end_date, store_id=store_id)",
    "purchase_report = ReportService.get_purchase_report(db, start_date, end_date, store_id=store_id, company_id=company_id)"
)

# Add company_id to get_profit_report
text = re.sub(
    r"def get_profit_report\(\s*db:\s*Session,\s*start_date:\s*Optional\[date\]\s*=\s*None,\s*end_date:\s*Optional\[date\]\s*=\s*None,\s*store_id:\s*Optional\[int\]\s*=\s*None\s*\)",
    "def get_profit_report(\n        db: Session,\n        start_date: Optional[date] = None,\n        end_date: Optional[date] = None,\n        store_id: Optional[int] = None,\n        company_id: Optional[int] = None\n    )",
    text
)

if "inv_query = inv_query.filter(_company_filter(Invoice, company_id))" not in text:
    text = text.replace(
        "if store_id is not None:\n            inv_query = inv_query.filter(Invoice.store_id == store_id)",
        "if store_id is not None:\n            inv_query = inv_query.filter(Invoice.store_id == store_id)\n        inv_query = inv_query.filter(_company_filter(Invoice, company_id))",
        1
    )
    text = text.replace(
        "if store_id is not None:\n            gold_calc_q = gold_calc_q.filter(Invoice.store_id == store_id)",
        "if store_id is not None:\n            gold_calc_q = gold_calc_q.filter(Invoice.store_id == store_id)\n        gold_calc_q = gold_calc_q.filter(_company_filter(Invoice, company_id))",
        1
    )
    text = text.replace(
        "if store_id is not None:\n            silver_calc_q = silver_calc_q.filter(Invoice.store_id == store_id)",
        "if store_id is not None:\n            silver_calc_q = silver_calc_q.filter(Invoice.store_id == store_id)\n        silver_calc_q = silver_calc_q.filter(_company_filter(Invoice, company_id))",
        1
    )
    text = text.replace(
        "if store_id is not None:\n            exc_q = exc_q.filter(Exchange.store_id == store_id)",
        "if store_id is not None:\n            exc_q = exc_q.filter(Exchange.store_id == store_id)\n        exc_q = exc_q.filter(_company_filter(Exchange, company_id))",
        1
    )
    text = text.replace(
        "if store_id is not None:\n            exc_new_q = exc_new_q.filter(Exchange.store_id == store_id)",
        "if store_id is not None:\n            exc_new_q = exc_new_q.filter(Exchange.store_id == store_id)\n        exc_new_q = exc_new_q.filter(_company_filter(Exchange, company_id))",
        1
    )

# Add company_id to get_dashboard_metrics
text = re.sub(
    r"def get_dashboard_metrics\(\s*db:\s*Session,\s*store_id:\s*Optional\[int\]\s*=\s*None\s*\)",
    "def get_dashboard_metrics(\n        db: Session,\n        store_id: Optional[int] = None,\n        company_id: Optional[int] = None\n    )",
    text
)
text = text.replace(
    "ReportService.get_sales_report(db, start_date=today, end_date=today, store_id=store_id)",
    "ReportService.get_sales_report(db, start_date=today, end_date=today, store_id=store_id, company_id=company_id)"
)
text = text.replace(
    "ReportService.get_purchase_report(db, start_date=today, end_date=today, store_id=store_id)",
    "ReportService.get_purchase_report(db, start_date=today, end_date=today, store_id=store_id, company_id=company_id)"
)
text = text.replace(
    "ReportService.get_profit_report(db, start_date=today, end_date=today, store_id=store_id)",
    "ReportService.get_profit_report(db, start_date=today, end_date=today, store_id=store_id, company_id=company_id)"
)

# Add company_id to get_dashboard_charts_data
text = re.sub(
    r"def get_dashboard_charts_data\(\s*db:\s*Session,\s*store_id:\s*Optional\[int\]\s*=\s*None\s*\)",
    "def get_dashboard_charts_data(\n        db: Session,\n        store_id: Optional[int] = None,\n        company_id: Optional[int] = None\n    )",
    text
)
if "trend_query = trend_query.filter(_company_filter(Invoice, company_id))" not in text:
    text = text.replace(
        "trend_query = trend_query.filter(Invoice.store_id == store_id)",
        "trend_query = trend_query.filter(Invoice.store_id == store_id)\n        trend_query = trend_query.filter(_company_filter(Invoice, company_id))"
    )

with open(p_rep_svc, "w", encoding="utf-8") as f:
    f.write(text)
print("Updated report_service.py with company isolation")

# 2. Update backend/app/api/v1/reports.py
p_reports_api = r"C:\Users\YASH SONI\Desktop\jeweller-app\backend\app\api\v1\reports.py"
with open(p_reports_api, "r", encoding="utf-8") as f:
    r_text = f.read()

# Helper resolver pattern in reports endpoints
endpoints = [
    ("def get_sales_report", "ReportService.get_sales_report(db, start_date, end_date, store_id=store_id, company_id=resolved_cid)"),
    ("def get_purchase_report", "ReportService.get_purchase_report(db, start_date, end_date, store_id=store_id, company_id=resolved_cid)"),
    ("def get_gst_report", "ReportService.get_gst_report(db, start_date, end_date, store_id=store_id, company_id=resolved_cid)"),
    ("def get_profit_report", "ReportService.get_profit_report(db, start_date, end_date, store_id=store_id, company_id=resolved_cid)"),
    ("def get_metal_flow_report", "ReportService.get_metal_flow_report(db, start_date, end_date, store_id=store_id, company_id=resolved_cid)"),
]

for fn_name, call_repl in endpoints:
    pattern = rf"({fn_name}\s*\(\s*start_date:\s*Optional\[date\]\s*=\s*Query\(None\),\s*end_date:\s*Optional\[date\]\s*=\s*Query\(None\),)"
    replacement = rf"\1\n    company_id: Optional[int] = Query(None),\n    x_company_id: Optional[str] = Header(None, alias=\"X-Company-ID\"),"
    r_text = re.sub(pattern, replacement, r_text)

# Add resolution block in each endpoint body
resolve_snippet = """    store_id = require_tenant_id(current_user)
    resolved_cid = company_id
    if not resolved_cid and x_company_id and x_company_id.isdigit():
        resolved_cid = int(x_company_id)
    if not resolved_cid:
        resolved_cid = 1"""

r_text = r_text.replace("store_id = require_tenant_id(current_user)\n    return ReportService.get_sales_report(db, start_date, end_date, store_id=store_id)",
                        f"{resolve_snippet}\n    return ReportService.get_sales_report(db, start_date, end_date, store_id=store_id, company_id=resolved_cid)")

r_text = r_text.replace("store_id = require_tenant_id(current_user)\n    return ReportService.get_purchase_report(db, start_date, end_date, store_id=store_id)",
                        f"{resolve_snippet}\n    return ReportService.get_purchase_report(db, start_date, end_date, store_id=store_id, company_id=resolved_cid)")

r_text = r_text.replace("store_id = require_tenant_id(current_user)\n    return ReportService.get_gst_report(db, start_date, end_date, store_id=store_id)",
                        f"{resolve_snippet}\n    return ReportService.get_gst_report(db, start_date, end_date, store_id=store_id, company_id=resolved_cid)")

r_text = r_text.replace("store_id = require_tenant_id(current_user)\n    return ReportService.get_profit_report(db, start_date, end_date, store_id=store_id)",
                        f"{resolve_snippet}\n    return ReportService.get_profit_report(db, start_date, end_date, store_id=store_id, company_id=resolved_cid)")

r_text = r_text.replace("store_id = require_tenant_id(current_user)\n    return ReportService.get_metal_flow_report(db, start_date, end_date, store_id=store_id)",
                        f"{resolve_snippet}\n    return ReportService.get_metal_flow_report(db, start_date, end_date, store_id=store_id, company_id=resolved_cid)")

with open(p_reports_api, "w", encoding="utf-8") as f:
    f.write(r_text)
print("Updated reports.py endpoints with company resolution")

# 3. Update dashboard.py
p_dash = r"C:\Users\YASH SONI\Desktop\jeweller-app\backend\app\api\v1\dashboard.py"
with open(p_dash, "r", encoding="utf-8") as f:
    d_text = f.read()

d_text = d_text.replace(
    "return ReportService.get_dashboard_metrics(db, store_id=store_id)",
    "return ReportService.get_dashboard_metrics(db, store_id=store_id, company_id=active_company)"
)
d_text = d_text.replace(
    "return ReportService.get_dashboard_charts_data(db, store_id=store_id)",
    "return ReportService.get_dashboard_charts_data(db, store_id=store_id, company_id=active_company)"
)
with open(p_dash, "w", encoding="utf-8") as f:
    f.write(d_text)
print("Updated dashboard.py metrics and charts with company_id")
