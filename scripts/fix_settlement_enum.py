import sqlite3

def fix_enum_in_invoice_py():
    path = r"C:\Users\YASH SONI\Desktop\jeweller-app\backend\app\models\invoice.py"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    target = """class SettlementType(str, enum.Enum):
    CASH = "Cash"
    METAL = "Metal\""""

    replacement = """class SettlementType(str, enum.Enum):
    CASH = "Cash"
    METAL = "Metal"
    HYBRID = "Hybrid"
    METAL_DUE = "metal_due"
    CASH_DUE = "cash_due"
    BOTH = "Both\""""

    if target in content:
        content = content.replace(target, replacement)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print("Updated SettlementType Enum in invoice.py")
    else:
        print("SettlementType Enum target not found or already updated")

def fix_db_settlement_type():
    db_path = r"C:\Users\YASH SONI\JewelleryERP_Data\jewellery_erp.db"
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute("UPDATE invoices SET settlement_type = 'Metal' WHERE settlement_type = 'metal_due'")
    con.commit()
    print(f"Fixed {cur.rowcount} rows in jewellery_erp.db invoices table")
    con.close()

if __name__ == "__main__":
    fix_enum_in_invoice_py()
    fix_db_settlement_type()
