import re

with open('src/screens/crm/CustomersScreen.tsx', 'r', encoding='utf-8') as f:
    txt = f.read()

txt = txt.replace("netOutstanding.toLocaleString('en-IN')", "formatAmount(netOutstanding)")
txt = txt.replace("(item.outstanding_balance || 0).toLocaleString('en-IN')", "formatAmount(item.outstanding_balance || 0)")
txt = txt.replace("(item.credit_limit || 0).toLocaleString('en-IN')", "formatAmount(item.credit_limit || 0)")

with open('src/screens/crm/CustomersScreen.tsx', 'w', encoding='utf-8') as f:
    f.write(txt)
