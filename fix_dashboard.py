import re

with open('src/screens/dashboard/DashboardScreen.tsx', 'r', encoding='utf-8') as f:
    txt = f.read()

txt = txt.replace(
    "navigation.navigate('Suppliers');",
    "navigation.navigate('Customers', { initialTab: 'suppliers' });"
)
txt = txt.replace(
    "navigation.navigate('Customers');",
    "navigation.navigate('Customers', { initialTab: 'customers' });"
)

with open('src/screens/dashboard/DashboardScreen.tsx', 'w', encoding='utf-8') as f:
    f.write(txt)
