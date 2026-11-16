from pathlib import Path
import re

main_file = Path(r"c:\Users\YASH SONI\Desktop\jeweller-app\desktop\src\main.js")
code = main_file.read_text(encoding="utf-8")

old_block = """ipcMain.handle('save-vault-pdf', async (_, { category, folderName, fileName, base64Data, isGst, companyId }) => {
  try {
    const isGstDoc = isGst || companyId === 2 || (fileName && (
      fileName.startsWith('SJ_S') || fileName.startsWith('SJ/S') ||
      fileName.startsWith('SJ_P') || fileName.startsWith('SJ/P') ||
      fileName.startsWith('SJ_E') || fileName.startsWith('SJ/E') ||
      fileName.startsWith('PG_') || fileName.includes('/S/') || fileName.includes('/P/') || fileName.includes('/E/')
    ));
    const gstSubfolder = isGstDoc ? 'GST' : 'Without_GST';

    const pcArchiveDir = path.join(pcDir, 'Archived_PDFs', gstSubfolder, category || 'Sales', folderName || 'Unknown');

    if (!fs.existsSync(pcArchiveDir)) {

      fs.mkdirSync(pcArchiveDir, { recursive: true });

    }

    const pcFilePath = path.join(pcArchiveDir, fileName);

    const buffer = Buffer.from(base64Data, 'base64');

    fs.writeFileSync(pcFilePath, buffer);"""

new_block = """ipcMain.handle('save-vault-pdf', async (_, { category, folderName, fileName, base64Data, isGst, companyId }) => {
  try {
    const cleanFileName = String(fileName || 'document.pdf').replace(/[\\\\/*?:"<>|]/g, '_').trim();
    const cleanFolderName = String(folderName || 'Unknown').replace(/[\\\\/*?:"<>|]/g, '_').trim();

    const isGstDoc = isGst || companyId === 2 || (cleanFileName && (
      cleanFileName.startsWith('SJ_S') || cleanFileName.startsWith('SJ/S') ||
      cleanFileName.startsWith('SJ_P') || cleanFileName.startsWith('SJ/P') ||
      cleanFileName.startsWith('SJ_E') || cleanFileName.startsWith('SJ/E') ||
      cleanFileName.startsWith('PG_') || cleanFileName.includes('_S_') || cleanFileName.includes('_P_') || cleanFileName.includes('_E_')
    ));
    const gstSubfolder = isGstDoc ? 'GST' : 'Without_GST';

    const pcArchiveDir = path.join(pcDir, 'Archived_PDFs', gstSubfolder, category || 'Sales', cleanFolderName);
    if (!fs.existsSync(pcArchiveDir)) {
      fs.mkdirSync(pcArchiveDir, { recursive: true });
    }

    const pcFilePath = path.join(pcArchiveDir, cleanFileName);
    const buffer = Buffer.from(base64Data, 'base64');
    fs.writeFileSync(pcFilePath, buffer);"""

code = code.replace(old_block, new_block)

# Also ensure USB path uses cleanFolderName and cleanFileName
old_usb = """        const usbArchiveDir = path.join(drive.letter, 'JewelleryERP_Data', 'Archived_PDFs', gstSubfolder, category || 'Sales', folderName || 'Unknown');
        if (!fs.existsSync(usbArchiveDir)) {
          fs.mkdirSync(usbArchiveDir, { recursive: true });
        }
        const usbFilePath = path.join(usbArchiveDir, fileName);"""

new_usb = """        const usbArchiveDir = path.join(drive.letter, 'JewelleryERP_Data', 'Archived_PDFs', gstSubfolder, category || 'Sales', cleanFolderName);
        if (!fs.existsSync(usbArchiveDir)) {
          fs.mkdirSync(usbArchiveDir, { recursive: true });
        }
        const usbFilePath = path.join(usbArchiveDir, cleanFileName);"""

code = code.replace(old_usb, new_usb)

main_file.write_text(code, encoding="utf-8")
print("desktop/src/main.js updated with cleanFileName and cleanFolderName!")
