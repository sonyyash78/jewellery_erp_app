from pathlib import Path
import re

main_file = Path(r"c:\Users\YASH SONI\Desktop\jeweller-app\desktop\src\main.js")
code = main_file.read_text(encoding="utf-8")

pattern = r"ipcMain\.handle\('save-vault-pdf', async \(_, \{ category, folderName, fileName, base64Data \}\) => \{\s*try \{\s*const pcArchiveDir = path\.join\(pcDir, 'Archived_PDFs', category \|\| 'Sales', folderName \|\| 'Unknown'\);"

replacement = """ipcMain.handle('save-vault-pdf', async (_, { category, folderName, fileName, base64Data, isGst, companyId }) => {
  try {
    const isGstDoc = isGst || companyId === 2 || (fileName && (
      fileName.startsWith('SJ_S') || fileName.startsWith('SJ/S') ||
      fileName.startsWith('SJ_P') || fileName.startsWith('SJ/P') ||
      fileName.startsWith('SJ_E') || fileName.startsWith('SJ/E') ||
      fileName.startsWith('PG_') || fileName.includes('/S/') || fileName.includes('/P/') || fileName.includes('/E/')
    ));
    const gstSubfolder = isGstDoc ? 'GST' : 'Without_GST';

    const pcArchiveDir = path.join(pcDir, 'Archived_PDFs', gstSubfolder, category || 'Sales', folderName || 'Unknown');"""

new_code, n = re.subn(pattern, replacement, code)
print(f"Replaced {n} occurrences in desktop/src/main.js")
if n > 0:
    main_file.write_text(new_code, encoding="utf-8")
    print("Saved main.js successfully!")
