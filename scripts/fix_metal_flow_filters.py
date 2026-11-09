with open('backend/app/services/report_service.py', 'r', encoding='utf-8') as f:
    c = f.read()

# 1. g_inv_q
t1 = """        if store_id is not None:
            g_inv_q = g_inv_q.filter(Invoice.store_id == store_id)
        if start_dt:"""
r1 = """        if store_id is not None:
            g_inv_q = g_inv_q.filter(Invoice.store_id == store_id)
        if company_id is not None:
            g_inv_q = g_inv_q.filter(_company_filter(Invoice, company_id))
        if start_dt:"""
if t1 in c:
    c = c.replace(t1, r1, 1)
    print("Added company_id filter to g_inv_q")

# 2. pur_gold_given_q
t2 = """        if store_id is not None:
            pur_gold_given_q = pur_gold_given_q.filter(Purchase.store_id == store_id)
        if start_dt:"""
r2 = """        if store_id is not None:
            pur_gold_given_q = pur_gold_given_q.filter(Purchase.store_id == store_id)
        if company_id is not None:
            pur_gold_given_q = pur_gold_given_q.filter(_company_filter(Purchase, company_id))
        if start_dt:"""
if t2 in c:
    c = c.replace(t2, r2, 1)
    print("Added company_id filter to pur_gold_given_q")

# 3. pur_silver_given_q
t3 = """        if store_id is not None:
            pur_silver_given_q = pur_silver_given_q.filter(Purchase.store_id == store_id)
        if start_dt:"""
r3 = """        if store_id is not None:
            pur_silver_given_q = pur_silver_given_q.filter(Purchase.store_id == store_id)
        if company_id is not None:
            pur_silver_given_q = pur_silver_given_q.filter(_company_filter(Purchase, company_id))
        if start_dt:"""
if t3 in c:
    c = c.replace(t3, r3, 1)
    print("Added company_id filter to pur_silver_given_q")

with open('backend/app/services/report_service.py', 'w', encoding='utf-8') as f:
    f.write(c)
print("Finished updating report_service.py")
