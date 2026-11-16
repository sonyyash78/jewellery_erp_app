from pathlib import Path
import re

backup_file = Path(r"c:\Users\YASH SONI\Desktop\jeweller-app\backend\app\api\v1\backup.py")
code = backup_file.read_text(encoding="utf-8")

code = re.sub(
    r'class SaveVaultPdfRequest\(BaseModel\):.*?(?=@router\.post\("/save-vault-pdf"\))',
    '''class SaveVaultPdfRequest(BaseModel):
    category: str
    folder_name: str
    file_name: str
    pdf_base64: str
    is_gst: Optional[bool] = None
    company_id: Optional[int] = None

''',
    code,
    flags=re.DOTALL
)

code = re.sub(
    r'usb_dir = Path\(f"\{letter\}:/JewelleryERP_Data/Archived_PDFs/\{category\}/\{folder\}"\)',
    'usb_dir = Path(f"{letter}:/JewelleryERP_Data/Archived_PDFs/{gst_subfolder}/{category}/{folder}")',
    code
)

backup_file.write_text(code, encoding="utf-8")
print("Cleanly updated backup.py!")
