paths = [
    r'C:\Users\YASH SONI\Desktop\jeweller-app\frontend\src\components\layout\AdminLayout.tsx',
    r'C:\Users\YASH SONI\Desktop\Saideep\jewellery-erp\frontend\src\components\layout\AdminLayout.tsx'
]

for p in paths:
    with open(p, 'r', encoding='utf-8') as f:
        c = f.read()

    # Add imports
    if 'import StartupCompanyModal' not in c:
        c = c.replace(
            "import AIAssistant from '../ai/AIAssistant';",
            "import AIAssistant from '../ai/AIAssistant';\nimport CompanySelector from '../common/CompanySelector';\nimport StartupCompanyModal from '../common/StartupCompanyModal';"
        )

    # Add StartupCompanyModal next to AIAssistant
    if '<StartupCompanyModal />' not in c:
        c = c.replace(
            '<AIAssistant />',
            '<StartupCompanyModal />\n      <AIAssistant />'
        )

    # Add CompanySelector to navbar
    if '<CompanySelector />' not in c:
        target_nav = '<div className="flex items-center space-x-1.5 sm:space-x-3 shrink-0">'
        c = c.replace(
            target_nav,
            target_nav + '\n            <CompanySelector />'
        )

    with open(p, 'w', encoding='utf-8') as f:
        f.write(c)

print('Surgically updated AdminLayout.tsx in both repos')
