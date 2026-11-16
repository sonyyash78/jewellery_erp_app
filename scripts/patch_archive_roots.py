file_path = r"C:\Users\YASH SONI\Desktop\jeweller-app\backend\app\services\pdf_archive_service.py"
with open(file_path, "r", encoding="utf-8") as f:
    text = f.read()

target = '    seen = {str(DATA_DIR).lower()}'
replacement = '''    seen = {str(DATA_DIR).lower()}

    # Also mirror to Downloads backup vault if present
    backup_vault = Path.home() / "Downloads" / "JewelleryERP_Backups" / "JewelleryERP_Data"
    if backup_vault.exists() and str(backup_vault).lower() not in seen:
        roots.append(backup_vault)
        seen.add(str(backup_vault).lower())'''

if target in text:
    text = text.replace(target, replacement, 1)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(text)
    print("Updated get_all_archive_roots successfully!")
else:
    print("Target not found!")
