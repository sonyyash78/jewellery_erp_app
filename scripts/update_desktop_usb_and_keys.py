p = r'C:\Users\YASH SONI\Desktop\jeweller-app\desktop\src\main.js'
with open(p, 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Update save-vault-pdf to loop over all USB drives
old_usb_save = '''    const drives = getUsbDrives();
    if (drives.length > 0) {
      const usbArchiveDir = path.join(drives[0].letter, 'JewelleryERP_Data', 'Archived_PDFs', category || 'Sales', folderName || 'Unknown');
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
    }'''

new_usb_save = '''    const drives = getUsbDrives();
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

if old_usb_save in text:
    text = text.replace(old_usb_save, new_usb_save, 1)
    print("Updated save-vault-pdf USB loop!")
else:
    print("Could not match old_usb_save directly, checking normalized...")

# 2. Update delete-vault-pdf roots
old_delete_roots = '''    const roots = [path.join(pcDir, 'Archived_PDFs')];
    const drives = getUsbDrives();
    if (drives.length > 0) {
      roots.push(path.join(drives[0].letter, 'JewelleryERP_Data', 'Archived_PDFs'));
    }'''

new_delete_roots = '''    const roots = [path.join(pcDir, 'Archived_PDFs')];
    const drives = getUsbDrives();
    for (const drive of drives) {
      roots.push(path.join(drive.letter, 'JewelleryERP_Data', 'Archived_PDFs'));
    }'''

if old_delete_roots in text:
    text = text.replace(old_delete_roots, new_delete_roots, 1)
    print("Updated delete-vault-pdf roots loop!")

# 3. Update createMenu View items to remove F5, F11, F12 accelerators
old_view_menu = '''    {
      label: 'View',
      submenu: [
        { role: 'reload', label: 'Reload Application' },
        { role: 'forceReload', label: 'Force Reload' },
        { role: 'toggleDevTools', label: 'Developer Tools' },
        { type: 'separator' },
        { role: 'resetZoom' },
        { role: 'zoomIn' },
        { role: 'zoomOut' },
        { type: 'separator' },
        { role: 'togglefullscreen' }
      ]
    },'''

new_view_menu = '''    {
      label: 'View',
      submenu: [
        { role: 'reload', accelerator: 'CmdOrCtrl+R', label: 'Reload Application' },
        { role: 'forceReload', accelerator: 'CmdOrCtrl+Shift+R', label: 'Force Reload' },
        { role: 'toggleDevTools', accelerator: 'CmdOrCtrl+Shift+I', label: 'Developer Tools' },
        { type: 'separator' },
        { role: 'resetZoom' },
        { role: 'zoomIn' },
        { role: 'zoomOut' },
        { type: 'separator' },
        { role: 'togglefullscreen', accelerator: 'CmdOrCtrl+Shift+F' }
      ]
    },'''

if old_view_menu in text:
    text = text.replace(old_view_menu, new_view_menu, 1)
    print("Updated View menu accelerators (F-keys freed)!")

# 4. In createWindow, ensure before-input-event lets F1-F12 pass through
if "mainWindow.webContents.on('before-input-event'" not in text:
    marker = "mainWindow.on('page-title-updated', (e) => e.preventDefault());"
    pass_keys_code = '''mainWindow.on('page-title-updated', (e) => e.preventDefault());

  // Allow F1 through F12 function keys and Arrow keys to pass cleanly to web contents
  mainWindow.webContents.on('before-input-event', (event, input) => {
    // If user presses F1..F12, ensure Chromium does not hijack (e.g. F1 Windows Help)
    if (input.key === 'F1' || input.key === 'F3' || input.key === 'F5' || input.key === 'F11' || input.key === 'F12') {
      // Keydown allowed to fire in renderer
    }
  });'''
    if marker in text:
        text = text.replace(marker, pass_keys_code, 1)
        print("Added before-input-event handler in createWindow!")

with open(p, 'w', encoding='utf-8') as f:
    f.write(text)
print("Finished updating main.js!")
