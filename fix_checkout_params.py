import re

with open('src/screens/purchases/CheckoutPurchaseScreen.tsx', 'r', encoding='utf-8') as f:
    txt = f.read()

txt = txt.replace('const { seller, items } = route.params;', 'const { selectedSeller: seller, items } = route.params;')

with open('src/screens/purchases/CheckoutPurchaseScreen.tsx', 'w', encoding='utf-8') as f:
    f.write(txt)
