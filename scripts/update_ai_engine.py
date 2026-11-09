import re

def fix_ai_report_call():
    path = r"C:\Users\YASH SONI\Desktop\jeweller-app\backend\app\api\v1\ai.py"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    target = "wastage_rep = ReportService.get_wastage_profit_report(db, company_id=1)"
    replacement = "wastage_rep = ReportService.get_company_wastage_analysis(db, company_id=1)"

    if target in content:
        content = content.replace(target, replacement)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print("[AI] Fixed ReportService.get_company_wastage_analysis in ai.py")
    else:
        print("[AI] Target not found")

if __name__ == "__main__":
    fix_ai_report_call()
