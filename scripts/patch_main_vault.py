from pathlib import Path
import re

main_file = Path(r"c:\Users\YASH SONI\Desktop\jeweller-app\desktop\src\main.js")
code = main_file.read_text(encoding="utf-8")

old_handler = """ipcMain.handle('save-vault-pdf', async (_, { category, folderName, fileName, base64Data }) => {
  try {
    const pcArchiveDir = path.join(pcDir, 'Archived_PDFs', category || 'Sales', folderName || 'Unknown');"""

new_handler = """ipcMain.handle('save-vault-pdf', async (_, { category, folderName, fileName, base64Data, isGst, companyId }) => {
  try {
    const isGstDoc = isGst || companyId === 2 || (fileName && (
      fileName.startsWith('SJ_S') || fileName.startsWith('SJ/S') ||
      fileName.startsWith('SJ_P') || fileName.startsWith('SJ/P') ||
      fileName.startsWith('SJ_E') || fileName.startsWith('SJ/E') ||
      fileName.startsWith('PG_') || fileName.includes('/S/') || fileName.includes('/P/') || fileName.includes('/E/')
    ));
    const gstSubfolder = isGstDoc ? 'GST' : 'Without_GST';

    const pcArchiveDir = path.join(pcDir, 'Archived_PDFs', gstSubfolder, category || 'Sales', folderName || 'Unknown');"""

if old_handler in code:
    code = code.replace(old_handler, new_handler)
    print("Updated pcArchiveDir in main.js")

old_usb_dir = """const usbArchiveDir = path.join(drive.letter, 'JewelleryERP_Data', 'Archived_PDFs', category || 'Sales', folderName || 'Unknown');"""
new_usb_dir = """const usbArchiveDir = path.join(drive.letter, 'JewelleryERP_Data', 'Archived_PDFs', gstSubfolder, category || 'Sales', folderName || 'Unknown');"""

if old_usb_dir in code:
    code = code.replace(old_usb_dir, new_usb_dir)
    print("Updated usbArchiveDir in main.js")

main_file.write_text(code, encoding="utf-8")
print("desktop/src/main.js updated successfully!")
