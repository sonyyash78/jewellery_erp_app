import re

with open('src/screens/crm/CustomersScreen.tsx', 'r', encoding='utf-8') as f:
    txt = f.read()

txt = txt.replace(
    'customerName: `${item.first_name} ${item.last_name || ""}`.trim(),',
    'customerName: `${item.first_name} ${item.last_name || ""}`.trim(), item: item,'
)

with open('src/screens/crm/CustomersScreen.tsx', 'w', encoding='utf-8') as f:
    f.write(txt)
