import os
import re

def fix_file(filepath):
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    
    new_content = content
    # Fix currency
    new_content = re.sub(r'\?(\{)', r'₹\1', new_content)
    new_content = re.sub(r'\?(\$\{)', r'₹\1', new_content)
    new_content = re.sub(r'\?([0-9])', r'₹\1', new_content)
    new_content = new_content.replace('? Balance', '₹ Balance')
    
    # Fix null names
    new_content = new_content.replace('`${item.first_name} ${item.last_name}`', '`${item.first_name} ${item.last_name || ""}`.trim()')
    new_content = new_content.replace('{item.first_name} {item.last_name}', '{item.first_name} {item.last_name || ""}')
    
    if new_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f'Fixed {filepath}')

for root, _, files in os.walk('src'):
    for file in files:
        if file.endswith('.tsx') or file.endswith('.ts'):
            fix_file(os.path.join(root, file))
