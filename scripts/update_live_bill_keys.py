path = r'C:\Users\YASH SONI\Desktop\jeweller-app\frontend\src\pages\billing\LiveBillSummary.tsx'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace("if (e.key === 'F7')", "if (e.key === 'F7' || e.key === 'F12')")
text = text.replace("GENERATE BILL (F7)", "GENERATE BILL (F12)")

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)
print('Updated LiveBillSummary.tsx successfully!')
