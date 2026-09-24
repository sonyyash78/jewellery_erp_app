import re

with open('src/screens/crm/CustomersScreen.tsx', 'r', encoding='utf-8') as f:
    txt = f.read()

txt = txt.replace('â€”', 'N/A')
txt = txt.replace('—', 'N/A')
txt = txt.replace('?"', 'N/A')

with open('src/screens/crm/CustomersScreen.tsx', 'w', encoding='utf-8') as f:
    f.write(txt)
