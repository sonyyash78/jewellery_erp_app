import re

with open('src/screens/crm/SupplierProfileScreen.tsx', 'r', encoding='utf-8') as f:
    txt = f.read()

txt = txt.replace('axiosClient.get(`/suppliers//bills`)', 'axiosClient.get(`/suppliers/${supplierId}/bills`)')
txt = txt.replace('axiosClient.get(`/customers/${supplierId}/bills`)', 'axiosClient.get(`/suppliers/${supplierId}/bills`)')

with open('src/screens/crm/SupplierProfileScreen.tsx', 'w', encoding='utf-8') as f:
    f.write(txt)
