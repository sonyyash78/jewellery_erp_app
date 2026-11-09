import re

p = r'C:\Users\YASH SONI\Desktop\jeweller-app\desktop\src\main.js'
with open(p, 'r', encoding='utf-8') as f:
    text = f.read()

pattern = r'const drives = getUsbDrives\(\);\s+if \(drives\.length > 0\) \{\s+const usbArchiveDir = path\.join\(drives\[0\]\.letter, \'JewelleryERP_Data\', \'Archived_PDFs\', category \|\| \'Sales\', folderName \|\| \'Unknown\'\);[\s\S]+?catch \(e\) \{\}\s+\}'

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
      } catch (usbErr) {
        console.warn(`[Vault USB Save Error on ${drive.letter}]`, usbErr.message);
      }
    }'''

match = re.search(pattern, text)
if match:
    text = text[:match.start()] + replacement + text[match.end():]
    with open(p, 'w', encoding='utf-8') as f:
        f.write(text)
    print("Successfully updated save-vault-pdf USB loop!")
else:
    print("Regex match failed for save-vault-pdf pattern")
