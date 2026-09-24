import re

with open('src/screens/exchange/CheckoutExchangeScreen.tsx', 'r', encoding='utf-8') as f:
    txt = f.read()

txt = txt.replace('const { customer, items } = route.params;', 'const { selectedCustomer: customer, items } = route.params;')

with open('src/screens/exchange/CheckoutExchangeScreen.tsx', 'w', encoding='utf-8') as f:
    f.write(txt)
