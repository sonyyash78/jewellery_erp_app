import re

with open('src/screens/crm/CustomersScreen.tsx', 'r', encoding='utf-8') as f:
    txt = f.read()

txt = txt.replace(
    "<Text style={styles.itemName}>{item.first_name} {item.last_name || ''}</Text>",
    "<Text style={styles.itemName}>{isCustomer ? `${item.first_name} ${item.last_name || ''}` : item.name}</Text>"
)

txt = txt.replace(
    'customerName: `${item.first_name} ${item.last_name || ""}`.trim(), item: item,',
    'customerName: isCustomer ? `${item.first_name} ${item.last_name || ""}`.trim() : item.name, item: item,'
)

txt = txt.replace(
    'supplierName: `${item.first_name} ${item.last_name || ""}`.trim()',
    'supplierName: isCustomer ? `${item.first_name} ${item.last_name || ""}`.trim() : item.name'
)

with open('src/screens/crm/CustomersScreen.tsx', 'w', encoding='utf-8') as f:
    f.write(txt)
