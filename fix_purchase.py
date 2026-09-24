import re

with open('src/screens/purchases/CreatePurchaseScreen.tsx', 'r', encoding='utf-8') as f:
    txt = f.read()

txt = re.sub(
    r'<TouchableOpacity style=\{styles\.customerOption\} onPress=\{\(\) => \{ setSelectedSeller\(null\); setShowSellerModal\(false\); \}\}>\s*<Text style=\{styles\.customerOptionText\}>-- Walk-in Supplier --</Text>\s*</TouchableOpacity>',
    '',
    txt
)

txt = re.sub(
    r'const handleSave = \(\) => \{\s*if \(items\.length === 0\) \{\s*Alert\.alert\(\'Error\', \'Please add at least one item\'\);\s*return;\s*\}',
    "const handleSave = () => {\n    if (items.length === 0) {\n      Alert.alert('Error', 'Please add at least one item');\n      return;\n    }\n    if (!selectedSeller) {\n      setShowSellerModal(true);\n      return;\n    }",
    txt
)

with open('src/screens/purchases/CreatePurchaseScreen.tsx', 'w', encoding='utf-8') as f:
    f.write(txt)
