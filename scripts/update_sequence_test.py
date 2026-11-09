import re

path = r"C:\Users\YASH SONI\Desktop\jeweller-app\tests\test_storage_and_sequence.py"
with open(path, "r", encoding="utf-8") as f:
    lines = f.readlines()

new_lines = []
for line in lines:
    new_lines.append(line)
    if "from app.models.company import CompanyNumberSequence" in line:
        new_lines.append("        from app.models.invoice import Invoice\n")
        new_lines.append("        self.db.query(Invoice).filter(Invoice.invoice_number == 'SJ/S/01/26-27').delete()\n")
        new_lines.append("        self.db.commit()\n")

with open(path, "w", encoding="utf-8") as f:
    f.writelines(new_lines)
print("Updated test_storage_and_sequence.py")
