paths = [
    r'C:\Users\YASH SONI\Desktop\jeweller-app\frontend\src\components\layout\AdminLayout.tsx',
    r'C:\Users\YASH SONI\Desktop\Saideep\jewellery-erp\frontend\src\components\layout\AdminLayout.tsx'
]

for p in paths:
    with open(p, 'r', encoding='utf-8') as f:
        c = f.read()

    if 'import StartupCompanyModal' not in c:
        c = c.replace(
            "import CompanySelector from '../common/CompanySelector';",
            "import CompanySelector from '../common/CompanySelector';\nimport StartupCompanyModal from '../common/StartupCompanyModal';"
        )

    if '<StartupCompanyModal />' not in c:
        c = c.replace(
            '<AIAssistant />',
            '<StartupCompanyModal />\n      <AIAssistant />'
        )

    with open(p, 'w', encoding='utf-8') as f:
        f.write(c)

print('Updated AdminLayout.tsx in both repos')
