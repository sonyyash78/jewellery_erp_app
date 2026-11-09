path = r'C:\Users\YASH SONI\Desktop\jeweller-app\backend\app\services\gst_pdf_template.py'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

old_stamp = """        <div class="stamp-box">
          <div style="font-size: 6pt;">★ PRIDE GOLD ★</div>
          <div style="font-size: 5.5pt;">JODHPUR</div>
        </div>"""

new_stamp = """        <div class="stamp-box">
          <div style="font-size: 6pt;">★ {co_name.upper()} ★</div>
          <div style="font-size: 5.5pt;">{(co_jurisdiction or "PALI").upper()}</div>
        </div>"""

if old_stamp in text:
    text = text.replace(old_stamp, new_stamp, 1)
else:
    # Try normalized
    for line in text.splitlines():
        if 'PRIDE GOLD' in line and 'stamp-box' in text:
            print('Line found:', line)

text = text.replace('★ PRIDE GOLD ★', '★ {co_name.upper()} ★')
text = text.replace('<div style="font-size: 5.5pt;">JODHPUR</div>', '<div style="font-size: 5.5pt;">{(co_jurisdiction or "PALI").upper()}</div>')

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)
print('Updated stamp in gst_pdf_template.py!')
