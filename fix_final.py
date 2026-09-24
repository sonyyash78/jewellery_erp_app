import os

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    # Very literal exact replacements to guarantee no escaping issues
    new_content = content.replace('>\\? {', '>₹ {')
    new_content = new_content.replace('>? {', '>₹ {')
    new_content = new_content.replace('? {item', '₹ {item')
    new_content = new_content.replace('?{', '₹{')
    new_content = new_content.replace('?$ {', '₹$ {')
    
    # Also fix ExchangeScreen.tsx specific crash
    new_content = new_content.replace('item.total_old_metal_value.toFixed', '(item.total_old_value || 0).toFixed')
    new_content = new_content.replace('item.total_old_value.toFixed', '(item.total_old_value || 0).toFixed')
    new_content = new_content.replace('item.grand_total.toFixed', '(item.grand_total || 0).toFixed')
    new_content = new_content.replace('item.difference_amount.toFixed', '(item.difference_amount || 0).toFixed')
    
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f'Fixed {filepath}')

for root, _, files in os.walk('src'):
    for file in files:
        if file.endswith('.tsx') or file.endswith('.ts'):
            fix_file(os.path.join(root, file))
