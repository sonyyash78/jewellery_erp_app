import re

path = r'C:\Users\YASH SONI\Desktop\jeweller-app\desktop\src\main.js'
with open(path, 'r', encoding='utf-8') as f:
    code = f.read()

pattern = r'const drives = getUsbDrives\(\);\s+if \(drives\.length > 0\) \{[\s\S]*?fs\.writeFileSync\(usbFilePath, buffer\);[\s\S]*?\} catch \(e\) \{\}\s+\}'

replacement = '''const drives = getUsbDrives();
    for (const drive of drives) {
      try {
        const usbArchiveDir = path.join(drive.letter, 'JewelleryERP_Data', 'Archived_PDFs', category || 'Sales', folderName || 'Unknown');
        if (!fs.existsSync(usbArchiveDir)) {
          fs.mkdirSync(usbArchiveDir, { recursive: true });
        }
        const usbFilePath = path.join(usbArchiveDir, fileName);
        fs.writeFileSync(usbFilePath, buffer);

        try {
          const docBase = fileName.replace('.pdf', '');
          const uFiles = fs.readdirSync(usbArchiveDir);
          for (const f of uFiles) {
            if (f !== fileName && f.includes(docBase) && f.endsWith('.pdf')) {
              fs.unlinkSync(path.join(usbArchiveDir, f));
            }
          }
        } catch (e) {}
      } catch (errDrive) {
        log.warn(`[SaveVaultPdf] USB write error for ${drive.letter}:`, errDrive);
      }
    }'''

code_new, count = re.subn(pattern, replacement, code, count=1)
if count > 0:
    with open(path, 'w', encoding='utf-8') as f:
        f.write(code_new)
    print("Updated saveVaultPdf loop in desktop/src/main.js")
else:
    print("Pattern not matched!")
