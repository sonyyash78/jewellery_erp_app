from pathlib import Path

p = Path(r"c:\Users\YASH SONI\Desktop\jeweller-app\frontend\src\utils\invoicePdfUtils.ts")
code = p.read_text(encoding="utf-8")
code = code.replace("import('../../api/axiosClient')", "import('../api/axiosClient')")
p.write_text(code, encoding="utf-8")
print("Fixed relative import in invoicePdfUtils.ts!")
