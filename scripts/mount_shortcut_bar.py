with open('frontend/src/components/layout/AdminLayout.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

# Add import
old_import = "import StartupCompanyModal from '../common/StartupCompanyModal';"
new_import = """import StartupCompanyModal from '../common/StartupCompanyModal';
import ShortcutBar from '../common/ShortcutBar';"""

assert old_import in text, "old_import not found"
text = text.replace(old_import, new_import, 1)

# Add component
old_comp = "<AIAssistant />"
new_comp = """<AIAssistant />
      <ShortcutBar />"""

assert old_comp in text, "old_comp not found"
text = text.replace(old_comp, new_comp, 1)

with open('frontend/src/components/layout/AdminLayout.tsx', 'w', encoding='utf-8') as f:
    f.write(text)
print("Mounted ShortcutBar in AdminLayout.tsx successfully!")
