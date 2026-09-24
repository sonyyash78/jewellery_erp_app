import re

with open('src/navigation/AppNavigator.tsx', 'r', encoding='utf-8') as f:
    txt = f.read()

txt = txt.replace(
    "import SupplierProfileScreen from '../screens/crm/SupplierProfileScreen';",
    "import SupplierProfileScreen from '../screens/crm/SupplierProfileScreen';\nimport CreateSettlementScreen from '../screens/crm/CreateSettlementScreen';"
)

txt = txt.replace(
    '<Stack.Screen name="CreateCRM" component={CreateCRMScreen} options={{ title: \'Add Contact\' }} />',
    '<Stack.Screen name="CreateCRM" component={CreateCRMScreen} options={{ title: \'Add Contact\' }} />\n            <Stack.Screen name="CreateSettlement" component={CreateSettlementScreen} options={{ title: \'Record Settlement\' }} />'
)

with open('src/navigation/AppNavigator.tsx', 'w', encoding='utf-8') as f:
    f.write(txt)
