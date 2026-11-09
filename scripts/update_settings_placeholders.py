path = r'C:\Users\YASH SONI\Desktop\jeweller-app\frontend\src\pages\settings\index.tsx'
with open(path, 'r', encoding='utf-8') as f:
    text = f.read()

text = text.replace('placeholder="e.g. PRIDE GOLD or SAIDEEP JEWELLERS"', 'placeholder="e.g. SAIDEEP JEWELLERS"')
text = text.replace('placeholder="e.g. 0291-2640999, +91-9929562800"', 'placeholder="e.g. +91-9460820878"')
text = text.replace('placeholder="e.g. 08AEZPK5007N1ZS"', 'placeholder="e.g. 08BNUPK1610E1Z3"')
text = text.replace('placeholder="e.g. AEZPK5007N"', 'placeholder="e.g. BNUPK1610E"')
text = text.replace('placeholder="e.g. info.pridegoldjdr@gmail.com"', 'placeholder="e.g. saideepjewellers78@gmail.com"')

with open(path, 'w', encoding='utf-8') as f:
    f.write(text)
print('Updated settings/index.tsx placeholders!')
