import os

files_to_update = [
    'src/screens/crm/CreateCRMScreen.tsx',
    'src/screens/crm/CreateSettlementScreen.tsx',
    'src/screens/crm/CustomersScreen.tsx',
    'src/screens/crm/SupplierProfileScreen.tsx',
    'src/screens/crm/SuppliersScreen.tsx'
]

for filepath in files_to_update:
    if not os.path.exists(filepath):
        continue
    with open(filepath, 'r', encoding='utf-8') as f:
        txt = f.read()
    
    # Replace all /suppliers/ endpoints with /sellers/
    txt = txt.replace('/suppliers/', '/sellers/')
    txt = txt.replace('/suppliers/?search=', '/sellers/?search=')
    txt = txt.replace('`/suppliers/${item.id}`', '`/sellers/${item.id}`')
    txt = txt.replace('`/suppliers/${id}`', '`/sellers/${id}`')
    txt = txt.replace('`/suppliers/${id}/ledger`', '`/sellers/${id}/ledger`')
    txt = txt.replace('`/suppliers/${supplierId}/bills`', '`/sellers/${supplierId}/bills`')
    
    # In CustomersScreen, we might need to change array parsing back because /sellers/ returns { items: [...] } ?
    # Let's check backend list_sellers:
    # `total = query.count()`
    # `items = query.offset(skip).limit(limit).all()`
    # `return {"items": items, "total": total, ...}`
    # Ah! So /sellers/ DOES return an object with "items"!
    # Let's revert that array parsing specifically for suppRes in CustomersScreen just to be safe:
    if 'CustomersScreen.tsx' in filepath:
        txt = txt.replace(
            'setSuppliers(Array.isArray(suppRes.data) ? suppRes.data : suppRes.data.items || []);',
            'setSuppliers(suppRes.data.items || suppRes.data || []);'
        )
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(txt)
