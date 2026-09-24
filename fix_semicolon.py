import re

for filepath in ['src/screens/crm/CustomerProfileScreen.tsx', 'src/screens/crm/SupplierProfileScreen.tsx']:
    with open(filepath, 'r', encoding='utf-8') as f:
        txt = f.read()
    
    txt = txt.replace('");}>', '")}>')

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(txt)
