p = r"C:\Users\YASH SONI\Desktop\jeweller-app\backend\app\api\v1\reports.py"
with open(p, "r", encoding="utf-8") as f:
    c = f.read()

c = c.replace('alias=\\"X-Company-ID\\"', 'alias="X-Company-ID"')

with open(p, "w", encoding="utf-8") as f:
    f.write(c)

print("Fixed reports.py alias cleanly")
