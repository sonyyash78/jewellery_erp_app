import re

with open('src/navigation/AppNavigator.tsx', 'r', encoding='utf-8') as f:
    txt = f.read()

txt = txt.replace(
    "import CreateInventoryScreen from '../screens/inventory/CreateInventoryScreen';",
    "import CreateInventoryScreen from '../screens/inventory/CreateInventoryScreen';\nimport EditInventoryScreen from '../screens/inventory/EditInventoryScreen';"
)

txt = txt.replace(
    "<Stack.Screen name=\"CreateInventory\" component={CreateInventoryScreen} options={{ title: 'Add Item' }} />",
    "<Stack.Screen name=\"CreateInventory\" component={CreateInventoryScreen} options={{ title: 'Add Item' }} />\n            <Stack.Screen name=\"EditInventory\" component={EditInventoryScreen} options={{ title: 'Edit Item' }} />"
)

with open('src/navigation/AppNavigator.tsx', 'w', encoding='utf-8') as f:
    f.write(txt)
