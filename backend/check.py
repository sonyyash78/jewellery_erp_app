import json
with open('db_audit.json') as f:
    data = json.load(f)

with open('audit_report.md', 'w', encoding='utf-8') as out:
    out.write('# Complete Database Audit Report\n\n')
    
    out.write('## 1. Sales Invoices\n')
    tot_inv_val = 0
    tot_inv_g = 0
    for i in data['invoices']:
        tot_inv_val += i['total']
        tot_inv_g += i['gold']
        out.write(f"- Invoice #{i['id']} ({i['date']}) | Total: ₹{i['total']} | Gold Given: {i['gold']}g | Silver Given: {i['silver']}g\n")
    out.write(f"\n**Total from Invoices**: ₹{tot_inv_val}\n")
    out.write(f"**Total Gold Given via Invoices**: {tot_inv_g}g\n\n")

    out.write('## 2. Purchases\n')
    tot_pur_val = 0
    tot_pur_g = 0
    for p in data['purchases']:
        tot_pur_val += p['total']
        tot_pur_g += p['gold']
        out.write(f"- Purchase #{p['id']} ({p['date']}) | Total: ₹{p['total']} | Gold Received: {p['gold']}g | Silver Received: {p['silver']}g\n")
    out.write(f"\n**Total from Purchases**: ₹{tot_pur_val}\n")
    out.write(f"**Total Gold Received via Purchases**: {tot_pur_g}g\n\n")

    out.write('## 3. Exchanges\n')
    tot_exc_new = 0
    tot_exc_old = 0
    tot_exc_g_given = 0
    tot_exc_g_recv = 0
    for e in data['exchanges']:
        tot_exc_new += e['new_val']
        tot_exc_old += e['old_val']
        tot_exc_g_given += e['gold_given']
        tot_exc_g_recv += e['gold_recv']
        out.write(f"- Exchange #{e['id']} ({e['date']}) | New Value (Sale): ₹{e['new_val']} | Old Value (Purchase): ₹{e['old_val']} | Gold Given: {e['gold_given']}g | Gold Received: {e['gold_recv']}g\n")
    
    out.write(f"\n**Total Exchange New Items (Added to Sales)**: ₹{tot_exc_new}\n")
    out.write(f"**Total Exchange Old Items (Added to Purchases)**: ₹{tot_exc_old}\n")
    out.write(f"**Total Gold Given via Exchanges**: {tot_exc_g_given}g\n")
    out.write(f"**Total Gold Received via Exchanges**: {tot_exc_g_recv}g\n\n")

    out.write('## Overall System Totals\n')
    out.write(f"- **TOTAL SYSTEM SALES (Invoices + Exchange New)**: ₹{tot_inv_val + tot_exc_new}\n")
    out.write(f"- **TOTAL SYSTEM PURCHASES (Purchases + Exchange Old)**: ₹{tot_pur_val + tot_exc_old}\n")
    out.write(f"- **TOTAL GOLD GIVEN**: {tot_inv_g + tot_exc_g_given}g\n")
    out.write(f"- **TOTAL GOLD RECEIVED**: {tot_pur_g + tot_exc_g_recv}g\n")

print("Audit report generated as audit_report.md")
