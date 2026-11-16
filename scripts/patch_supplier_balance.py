from pathlib import Path

p = Path(r"c:\Users\YASH SONI\Desktop\jeweller-app\backend\app\services\pdf_archive_service.py")
code = p.read_text(encoding="utf-8")

code = code.replace(
    "float(s.current_balance or 0.0)",
    'float(getattr(s, "outstanding_balance", 0.0) or getattr(s, "current_balance", 0.0) or 0.0)'
)

p.write_text(code, encoding="utf-8")
print("Updated supplier balance attribute cleanly!")
