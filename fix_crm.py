import re

with open('src/screens/crm/CustomersScreen.tsx', 'r', encoding='utf-8') as f:
    txt = f.read()

# Fix 1: The Suppliers data array
txt = txt.replace(
    'setSuppliers(suppRes.data.items || []);',
    'setSuppliers(Array.isArray(suppRes.data) ? suppRes.data : suppRes.data.items || []);'
)

# Fix 2: Drawer Navigation Sync
drawer_sync = """  useEffect(() => {
    if (route.params?.initialTab) {
      setActiveTab(route.params.initialTab);
    }
  }, [route.params?.initialTab]);

  useFocusEffect("""
txt = txt.replace('  useFocusEffect(', drawer_sync)

with open('src/screens/crm/CustomersScreen.tsx', 'w', encoding='utf-8') as f:
    f.write(txt)
