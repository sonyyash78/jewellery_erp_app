import re

with open('src/screens/crm/CustomersScreen.tsx', 'r', encoding='utf-8') as f:
    txt = f.read()

txt = txt.replace(
    'const netOutstanding = customers.reduce((acc, c) => acc + (c.outstanding_balance || 0), 0);',
    'const netOutstanding = customers.reduce((acc, c) => acc + (parseFloat(c.outstanding_balance as any) || 0), 0);'
)

# Also fix the formatAmount function so it definitely returns a string without NaN string
txt = txt.replace(
    'const absNum = Math.abs(num);',
    'const absNum = Math.abs(parseFloat(num as any) || 0);'
)

with open('src/screens/crm/CustomersScreen.tsx', 'w', encoding='utf-8') as f:
    f.write(txt)
