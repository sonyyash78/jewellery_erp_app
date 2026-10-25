# Jewellery ERP - 100% Offline PC Desktop Application

Standalone native Windows desktop application for **Saideep Jewellers ERP**. Runs completely offline without any internet connection, cloud dependency, or third-party database server.

---

## 🚀 Quick Start (1-Click Launch)

### Option 1: Desktop Shortcut
A shortcut has been created directly on your Windows Desktop:
- Double-click **`Jewellery ERP`** on your Desktop.

### Option 2: Batch Launcher
Inside the `jewellery-erp` folder:
- Double-click **`start-desktop.bat`**.

---

## 🔑 Default Offline Login Credentials

When launching the app for the first time, your local database is automatically bootstrapped:
- **Username:** `admin`
- **Password:** `admin`

*(You can change your password and add additional staff accounts anytime inside Settings).*

---

## 💾 Local SQLite Database

Your data is stored safely on your PC in a single, high-performance SQLite database:
- **Path:** `%APPDATA%\jewellery-erp-desktop\data\jewellery_erp.db`
- **Full Path Example:** `C:\Users\<Your-Username>\AppData\Roaming\jewellery-erp-desktop\data\jewellery_erp.db`

### Zero Setup Required
- No MySQL installation needed.
- No cloud internet connection needed.
- Safe from cloud timeouts or cold starts.

---

## 📦 Database Backup & Restore

### Automatic 1-Click Backup from the App
1. Open **Jewellery ERP Desktop**.
2. From the top menu bar, click **File** &rarr; **Backup Database (.db)...** (or press `Ctrl + B`).
3. Choose where to save your backup (e.g. Pen Drive, External Hard Disk, Desktop, Documents).
4. Click **Save**.

### Open Data Folder
- From the menu bar, click **File** &rarr; **Open Data Folder in Explorer** to directly view the active `.db` database file.

---

## 🛠️ Build Standalone Windows Installer (.exe)

To build standalone Windows installers (`.exe` setup or portable `.exe`):

```bash
cd desktop
npm run dist
```

Outputs are generated in `desktop/dist-electron/`:
- `Jewellery ERP Desktop Setup 1.0.0.exe` (Full NSIS Windows Installer)
- `Jewellery ERP Desktop 1.0.0.exe` (Portable Single-file Executable)
