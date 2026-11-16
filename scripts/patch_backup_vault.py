from pathlib import Path
import re

backup_file = Path(r"c:\Users\YASH SONI\Desktop\jeweller-app\backend\app\api\v1\backup.py")
content = backup_file.read_text(encoding="utf-8")

# Update SaveVaultPdfRequest
old_cls = """class SaveVaultPdfRequest(BaseModel):
    category: str
    folder_name: str
    file_name: str
    pdf_base64: str"""

new_cls = """class SaveVaultPdfRequest(BaseModel):
    category: str
    folder_name: str
    file_name: str
    pdf_base64: str
    is_gst: Optional[bool] = None
    company_id: Optional[int] = None"""

if old_cls in content:
    content = content.replace(old_cls, new_cls)
    print("Updated SaveVaultPdfRequest class")

# Update target_dir in save_vault_pdf
old_target = """    target_dir = DATA_DIR / "Archived_PDFs" / category / folder"""
new_target = """    # Route to GST vs Without_GST
    is_gst = bool(payload.is_gst or payload.company_id == 2)
    if not is_gst and payload.file_name:
        fn_upper = payload.file_name.upper()
        if fn_upper.startswith(("SJ_S", "SJ/S", "SJ_P", "SJ/P", "SJ_E", "SJ/E", "PG_S", "PG/S", "PG_P", "PG/P", "PG_E", "PG/E")) or "/S/" in fn_upper or "/P/" in fn_upper or "/E/" in fn_upper:
            is_gst = True
    gst_subfolder = "GST" if is_gst else "Without_GST"

    target_dir = DATA_DIR / "Archived_PDFs" / gst_subfolder / category / folder"""

if old_target in content:
    content = content.replace(old_target, new_target)
    print("Updated target_dir in save_vault_pdf")

# Update USB target dir in save_vault_pdf
old_usb = """usb_dir = Path(f"{letter}:/JewelleryERP_Data/Archived_PDFs/{category}/{folder}")"""
new_usb = """usb_dir = Path(f"{letter}:/JewelleryERP_Data/Archived_PDFs/{gst_subfolder}/{category}/{folder}")"""

if old_usb in content:
    content = content.replace(old_usb, new_usb)
    print("Updated usb_dir in save_vault_pdf")

backup_file.write_text(content, encoding="utf-8")
print("backup.py updated successfully!")
