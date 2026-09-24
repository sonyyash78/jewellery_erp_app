import re

with open('src/screens/crm/CustomersScreen.tsx', 'r', encoding='utf-8') as f:
    txt = f.read()

txt = txt.replace("item.phone_number || 'N/A'", "item.phone_number || item.mobile || 'N/A'")

with open('src/screens/crm/CustomersScreen.tsx', 'w', encoding='utf-8') as f:
    f.write(txt)

# Do the same for CustomerProfileScreen & SupplierProfileScreen
for filepath in ['src/screens/crm/CustomerProfileScreen.tsx', 'src/screens/crm/SupplierProfileScreen.tsx']:
    with open(filepath, 'r', encoding='utf-8') as f:
        profile_txt = f.read()
    profile_txt = profile_txt.replace("item?.phone_number || 'N/A'", "item?.phone_number || item?.mobile || 'N/A'")
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(profile_txt)
