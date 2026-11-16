from pathlib import Path
import re

backup_file = Path(r"c:\Users\YASH SONI\Desktop\jeweller-app\backend\app\api\v1\backup.py")
code = backup_file.read_text(encoding="utf-8")

old_block = """    category = payload.category or "Sales"

    folder = payload.folder_name or "Unknown"

    filename = payload.file_name or "document.pdf"

    

    # Route to GST vs Without_GST
    is_gst = bool(payload.is_gst or payload.company_id == 2)
    if not is_gst and payload.file_name:
        fn_upper = payload.file_name.upper()
        if fn_upper.startswith(("SJ_S", "SJ/S", "SJ_P", "SJ/P", "SJ_E", "SJ/E", "PG_S", "PG/S", "PG_P", "PG/P", "PG_E", "PG/E")) or "/S/" in fn_upper or "/P/" in fn_upper or "/E/" in fn_upper:
            is_gst = True
    gst_subfolder = "GST" if is_gst else "Without_GST"

    target_dir = DATA_DIR / "Archived_PDFs" / gst_subfolder / category / folder

    target_dir.mkdir(parents=True, exist_ok=True)

    target_file = target_dir / filename"""

new_block = """    category = payload.category or "Sales"
    folder = payload.folder_name or "Unknown"
    filename = payload.file_name or "document.pdf"

    import re
    clean_filename = re.sub(r'[\\\\/*?:"<>|]', '_', filename).strip()
    clean_folder = re.sub(r'[\\\\/*?:"<>|]', '_', folder).strip()

    # Route to GST vs Without_GST
    is_gst = bool(payload.is_gst or payload.company_id == 2)
    if not is_gst and clean_filename:
        fn_upper = clean_filename.upper()
        if fn_upper.startswith(("SJ_S", "SJ/S", "SJ_P", "SJ/P", "SJ_E", "SJ/E", "PG_S", "PG/S", "PG_P", "PG/P", "PG_E", "PG/E")) or "/S/" in fn_upper or "_S_" in fn_upper or "/P/" in fn_upper or "_P_" in fn_upper or "/E/" in fn_upper or "_E_" in fn_upper:
            is_gst = True
    gst_subfolder = "GST" if is_gst else "Without_GST"

    target_dir = DATA_DIR / "Archived_PDFs" / gst_subfolder / category / clean_folder
    target_dir.mkdir(parents=True, exist_ok=True)
    target_file = target_dir / clean_filename"""

code = code.replace(old_block, new_block)

# Also update USB write
old_usb = """usb_dir = Path(f"{letter}:/JewelleryERP_Data/Archived_PDFs/{gst_subfolder}/{category}/{folder}")"""
new_usb = """usb_dir = Path(f"{letter}:/JewelleryERP_Data/Archived_PDFs/{gst_subfolder}/{category}/{clean_folder}")"""
code = code.replace(old_usb, new_usb)

old_usb_write = """(usb_dir / filename).write_bytes(pdf_bytes)"""
new_usb_write = """(usb_dir / clean_filename).write_bytes(pdf_bytes)"""
code = code.replace(old_usb_write, new_usb_write)

backup_file.write_text(code, encoding="utf-8")
print("backup.py updated with clean_filename and clean_folder!")
