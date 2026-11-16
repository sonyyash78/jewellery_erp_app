import sqlite3
import shutil
from datetime import datetime

primary_db = r"C:\Users\YASH SONI\JewelleryERP_Data\jewellery_erp.db"
backup_db = r"C:\Users\YASH SONI\Downloads\JewelleryERP_Backups\JewelleryERP_Data\jewellery_erp.db"

# 1. Create a safe backup before cleaning
ts = datetime.now().strftime("%Y%m%d_%H%M%S")
pre_bak = f"{primary_db}.bak_pre_clean_{ts}"
shutil.copy2(primary_db, pre_bak)
print(f"[Backup] Created pre-cleanup backup: {pre_bak}")

conn = sqlite3.connect(primary_db)
conn.row_factory = sqlite3.Row
cur = conn.cursor()

# 2. Get active invoice numbers
cur.execute("SELECT id, invoice_number, grand_total, cash_received, balance_amount, gold_balance_metal_weight FROM invoices WHERE status != 'Cancelled'")
invoices = cur.fetchall()
inv_nums = {row['invoice_number'] for row in invoices}
print(f"[Invoices] Active invoices count: {len(invoices)} -> {inv_nums}")

# 3. Clean orphan customer_ledgers
cur.execute("SELECT id, voucher_number, voucher_type, debit, credit, balance, gold_debit, gold_credit, gold_balance FROM customer_ledgers")
all_ledgers = cur.fetchall()
print(f"[Ledgers] Total existing customer_ledgers: {len(all_ledgers)}")

# Identify rows to keep vs delete
to_keep_ids = []
for l in all_ledgers:
    v_num = l['voucher_number']
    base_inv = v_num.replace("REV-", "")
    if base_inv in inv_nums:
        to_keep_ids.append(l['id'])
    else:
        print(f"  -> Deleting orphan ledger row id={l['id']}, voucher={v_num}, desc={l['voucher_type']}")

cur.execute(f"DELETE FROM customer_ledgers WHERE id NOT IN ({','.join(str(i) for i in to_keep_ids)})")
print(f"[Ledgers] Deleted {len(all_ledgers) - len(to_keep_ids)} orphan rows. Kept {len(to_keep_ids)} rows.")

# 4. Recalculate customer_ledgers running balances and customer totals
cur.execute("SELECT id, voucher_number, date FROM customer_ledgers ORDER BY date ASC, id ASC")
remaining_ledgers = cur.fetchall()

running_cash_bal = 0.0
running_gold_bal = 0.0
running_silver_bal = 0.0

for r in remaining_ledgers:
    r_id = r['id']
    v_num = r['voucher_number']
    if v_num == 'INV-20261109-0003':
        debit = 157786.0
        credit = 0.0
        running_cash_bal += (debit - credit)
        gold_deb = 0.0
        gold_crd = 0.0
        running_gold_bal += (gold_deb - gold_crd)
        cur.execute("""
            UPDATE customer_ledgers
            SET debit = ?, credit = ?, balance = ?,
                gold_debit = ?, gold_credit = ?, gold_balance = ?,
                silver_debit = 0, silver_credit = 0, silver_balance = ?,
                description = 'Bill INV-20261109-0003 (Cash)',
                company_id = 1
            WHERE id = ?
        """, (debit, credit, running_cash_bal, gold_deb, gold_crd, running_gold_bal, running_silver_bal, r_id))
    elif v_num == 'INV-20261109-0002':
        debit = 153305.0
        credit = 135720.0
        running_cash_bal += (debit - credit)
        gold_deb = 18.720
        gold_crd = 0.0
        running_gold_bal += (gold_deb - gold_crd)
        cur.execute("""
            UPDATE customer_ledgers
            SET debit = ?, credit = ?, balance = ?,
                gold_debit = ?, gold_credit = ?, gold_balance = ?,
                silver_debit = 0, silver_credit = 0, silver_balance = ?,
                description = 'Bill INV-20261109-0002 (Metal/Hybrid)',
                company_id = 1
            WHERE id = ?
        """, (debit, credit, running_cash_bal, gold_deb, gold_crd, running_gold_bal, running_silver_bal, r_id))

print(f"[Recalculate] Final Yash Balances -> Cash: {running_cash_bal}, Gold: {running_gold_bal}g")

# 5. Update customers table
cur.execute("""
    UPDATE customers
    SET outstanding_balance = ?,
        fine_gold_balance = ?,
        fine_silver_balance = 0
    WHERE id = 2
""", (running_cash_bal, running_gold_bal))
print("[Customer] Updated customer Yash (id=2) outstanding_balance and fine_gold_balance")

# 6. Clean orphan invoice_items and gold_calculations
cur.execute("DELETE FROM gold_calculations WHERE invoice_item_id IN (SELECT id FROM invoice_items WHERE invoice_id NOT IN (SELECT id FROM invoices))")
cur.execute("DELETE FROM invoice_items WHERE invoice_id NOT IN (SELECT id FROM invoices)")
print("[InvoiceItems] Cleaned orphan items from deleted test invoices")

# 7. Update supplier_ledgers company_id to match purchases
cur.execute("UPDATE supplier_ledgers SET company_id = 2 WHERE voucher_number = 'PUR-632746'")
cur.execute("UPDATE supplier_ledgers SET company_id = 1 WHERE voucher_number = 'PUR-320414'")
print("[SupplierLedgers] Updated company_id mapping for PUR-632746 and PUR-320414")

conn.commit()
conn.close()

# 8. Copy updated DB to backup vault
shutil.copy2(primary_db, backup_db)
print(f"[Sync] Copied cleaned DB to {backup_db}")
