import re

with open('src/screens/crm/CustomersScreen.tsx', 'r', encoding='utf-8') as f:
    txt = f.read()

# Fix the corrupted powershell currency symbol
txt = txt.replace(',1', '₹')
txt = txt.replace(',1 ', '₹ ')
txt = txt.replace(',1', '₹')
# Just in case there are other corruptions:
txt = txt.replace('â‚¹', '₹')

with open('src/screens/crm/CustomersScreen.tsx', 'w', encoding='utf-8') as f:
    f.write(txt)
