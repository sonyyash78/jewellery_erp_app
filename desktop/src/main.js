const { app, BrowserWindow, ipcMain, dialog, shell, Menu } = require('electron');
const path = require('path');
const fs = require('fs');
const http = require('http');
const { spawn, exec, execSync } = require('child_process');

// 1. Enforce STRICT Single Instance Lock — prevents infinite windows!
const gotTheLock = app.requestSingleInstanceLock();
if (!gotTheLock) {
  console.log('[Desktop] Another instance is already running. Quitting.');
  app.quit();
  process.exit(0);
}

let mainWindow = null;
let pythonProcess = null;
let isStartingWindow = false;

const BACKEND_PORT = 8000;
const BACKEND_URL = `http://127.0.0.1:${BACKEND_PORT}`;

// 2. Prepare Local Database Directories
// Primary: C:\Users\<Username>\JewelleryERP_Data (visible and accessible to user)
// Fallback: AppData\jewellery-erp-desktop\data
const homeDataDir = path.join(app.getPath('home'), 'JewelleryERP_Data');
const appDataDbDir = path.join(app.getPath('userData'), 'data');

let dbDir = homeDataDir;
try {
  if (!fs.existsSync(dbDir)) {
    fs.mkdirSync(dbDir, { recursive: true });
  }
} catch (e) {
  dbDir = appDataDbDir;
  if (!fs.existsSync(dbDir)) {
    fs.mkdirSync(dbDir, { recursive: true });
  }
}
const dbPath = path.join(dbDir, 'jewellery_erp.db');

// Resolve Backend directory & Standalone binary
const backendDir = app.isPackaged
  ? path.join(process.resourcesPath, 'backend')
  : path.resolve(__dirname, '../../backend');

const frontendDist = app.isPackaged
  ? path.join(process.resourcesPath, 'frontend/dist')
  : path.resolve(__dirname, '../../frontend/dist');

const standaloneBinary = app.isPackaged
  ? path.join(process.resourcesPath, 'bin/jewellery-backend/jewellery-backend.exe')
  : path.resolve(__dirname, '../bin/jewellery-backend/jewellery-backend.exe');

/**
 * Scan Windows for connected USB / Removable Drives
 */
function getUsbDrives() {
  const drives = [];
  try {
    if (process.platform === 'win32') {
      const output = execSync(
        'powershell -NoProfile -Command "Get-CimInstance Win32_LogicalDisk | Where-Object { $_.DriveType -eq 2 } | Select-Object -Property DeviceID, VolumeName | ConvertTo-Json"',
        { encoding: 'utf8', timeout: 3000 }
      );
      if (output && output.trim()) {
        const parsed = JSON.parse(output.trim());
        const list = Array.isArray(parsed) ? parsed : [parsed];
        for (const item of list) {
          if (item && item.DeviceID) {
            drives.push({
              letter: item.DeviceID,
              name: item.VolumeName ? `${item.DeviceID} (${item.VolumeName})` : `${item.DeviceID} (USB Drive)`
            });
          }
        }
      }
    }
  } catch (e) {
    console.log('[Desktop] Removable drive query info:', e.message);
  }
  return drives;
}

/**
 * Perform 1-Click Backup to Pendrive / USB
 */
async function backupToUsb(parentWin) {
  try {
    const drives = getUsbDrives();
    let targetDir = null;

    if (drives.length === 1) {
      targetDir = path.join(drives[0].letter, 'JewelleryERP_Backups');
    } else if (drives.length > 1) {
      const buttons = drives.map(d => d.name);
      buttons.push('Cancel');
      const res = await dialog.showMessageBox(parentWin, {
        type: 'question',
        title: 'Select USB Pendrive',
        message: 'Multiple USB drives detected. Choose destination drive:',
        buttons,
        defaultId: 0
      });
      if (res.response < drives.length) {
        targetDir = path.join(drives[res.response].letter, 'JewelleryERP_Backups');
      } else {
        return { success: false, cancelled: true };
      }
    } else {
      // Prompt user to select pendrive folder if auto-detection was empty
      const res = await dialog.showOpenDialog(parentWin, {
        title: 'Select USB Pendrive or Backup Folder',
        properties: ['openDirectory', 'createDirectory']
      });
      if (!res.canceled && res.filePaths.length > 0) {
        targetDir = path.join(res.filePaths[0], 'JewelleryERP_Backups');
      } else {
        return { success: false, cancelled: true };
      }
    }

    if (!fs.existsSync(targetDir)) {
      fs.mkdirSync(targetDir, { recursive: true });
    }

    const now = new Date();
    const pad = (n) => String(n).padStart(2, '0');
    const timestamp = `${now.getFullYear()}-${pad(now.getMonth()+1)}-${pad(now.getDate())}_${pad(now.getHours())}${pad(now.getMinutes())}`;
    const destFile = path.join(targetDir, `jewellery_erp_backup_${timestamp}.db`);
    const latestFile = path.join(targetDir, 'jewellery_erp_latest.db');

    if (fs.existsSync(dbPath)) {
      fs.copyFileSync(dbPath, destFile);
      fs.copyFileSync(dbPath, latestFile);
    }

    await dialog.showMessageBox(parentWin, {
      type: 'info',
      title: 'USB Backup Completed',
      message: `Database successfully copied to Pendrive!\n\nFolder: ${targetDir}\nFile: jewellery_erp_backup_${timestamp}.db\n\nYour data is completely safe and portable.`
    });

    return { success: true, path: destFile };
  } catch (err) {
    dialog.showErrorBox('Backup Error', `Failed to copy database: ${err.message}`);
    return { success: false, error: err.message };
  }
}

/**
 * Restore Database from Pendrive / File
 */
async function restoreDatabase(parentWin) {
  const res = await dialog.showOpenDialog(parentWin, {
    title: 'Select Backup Database (.db) to Restore',
    filters: [{ name: 'SQLite Database', extensions: ['db', 'sqlite', 'bak'] }],
    properties: ['openFile']
  });

  if (!res.canceled && res.filePaths.length > 0) {
    const selectedFile = res.filePaths[0];
    const confirm = await dialog.showMessageBox(parentWin, {
      type: 'warning',
      title: 'Confirm Database Restore',
      message: `Are you sure you want to restore from:\n${selectedFile}?\n\nCurrent local data will be replaced with this backup. The app will reload.`,
      buttons: ['Restore Now', 'Cancel'],
      defaultId: 1
    });

    if (confirm.response === 0) {
      if (fs.existsSync(dbPath)) {
        fs.copyFileSync(dbPath, `${dbPath}.bak_${Date.now()}`);
      }
      fs.copyFileSync(selectedFile, dbPath);
      dialog.showMessageBoxSync(parentWin, {
        type: 'info',
        title: 'Restore Completed',
        message: 'Database restored successfully! Reloading application...'
      });
      parentWin.reload();
      return { success: true };
    }
  }
  return { success: false, cancelled: true };
}

/**
 * Start the Backend process (Standalone binary or Python)
 */
function startBackend() {
  const env = {
    ...process.env,
    PYTHONUNBUFFERED: '1',
    DATABASE_URL: `sqlite:///${dbPath.replace(/\\/g, '/')}`,
    OFFLINE_MODE: 'true',
    ENVIRONMENT: 'offline',
    SECRET_KEY: 'jewellery-erp-desktop-offline-secret-key-2026',
    INITIAL_ADMIN_PASSWORD: 'admin',
    BACKEND_PORT: String(BACKEND_PORT),
    BACKEND_HOST: '127.0.0.1'
  };

  // Check if standalone binary exists (Zero-dependency portable mode!)
  if (fs.existsSync(standaloneBinary)) {
    console.log(`[Desktop] Spawning Standalone Backend: ${standaloneBinary}`);
    pythonProcess = spawn(standaloneBinary, [], {
      cwd: path.dirname(standaloneBinary),
      env,
      stdio: ['ignore', 'pipe', 'pipe']
    });
  } else {
    // Fallback: Python interpreter
    const pythonCmd = process.platform === 'win32' ? 'python' : 'python3';
    const scriptPath = path.join(backendDir, 'run_server.py');
    console.log(`[Desktop] Spawning Python interpreter for ${scriptPath}`);
    pythonProcess = spawn(
      pythonCmd,
      [scriptPath],
      {
        cwd: backendDir,
        env,
        stdio: ['ignore', 'pipe', 'pipe']
      }
    );
  }

  pythonProcess.stdout.on('data', (d) => console.log(`[Backend] ${d.toString().trim()}`));
  pythonProcess.stderr.on('data', (d) => console.error(`[Backend] ${d.toString().trim()}`));
  pythonProcess.on('exit', (code, signal) => {
    console.log(`[Desktop] Backend process exited (code=${code}, signal=${signal})`);
  });
}

/**
 * Poll http://127.0.0.1:8000/ping until ready
 */
function waitForBackend(callback, maxRetries = 40) {
  let attempts = 0;
  const check = () => {
    attempts++;
    const req = http.get(`${BACKEND_URL}/ping`, (res) => {
      if (res.statusCode === 200) {
        console.log('[Desktop] Backend is ready and responding!');
        callback(null);
      } else {
        retry();
      }
    });

    req.on('error', () => {
      retry();
    });

    req.setTimeout(600, () => {
      req.abort();
      retry();
    });
  };

  const retry = () => {
    if (attempts >= maxRetries) {
      callback(new Error('Backend initialization timed out'));
    } else {
      setTimeout(check, 300);
    }
  };

  check();
}

/**
 * Build Application Menu with Pendrive & Database Actions
 */
function createMenu() {
  const template = [
    {
      label: 'File',
      submenu: [
        {
          label: '💾 1-Click Backup to Pendrive / USB...',
          accelerator: 'CmdOrCtrl+U',
          click: () => {
            if (mainWindow) backupToUsb(mainWindow);
          }
        },
        {
          label: '💾 Save Database Backup As...',
          accelerator: 'CmdOrCtrl+B',
          click: async () => {
            const { filePath } = await dialog.showSaveDialog(mainWindow, {
              title: 'Backup Jewellery ERP Database',
              defaultPath: `jewellery_erp_backup_${new Date().toISOString().slice(0, 10)}.db`,
              filters: [{ name: 'SQLite Database', extensions: ['db', 'sqlite'] }]
            });
            if (filePath && fs.existsSync(dbPath)) {
              fs.copyFileSync(dbPath, filePath);
              dialog.showMessageBox(mainWindow, {
                type: 'info',
                title: 'Backup Successful',
                message: `Database successfully backed up to:\n${filePath}`
              });
            }
          }
        },
        {
          label: '🔄 Restore Database from Backup / Pendrive...',
          click: () => {
            if (mainWindow) restoreDatabase(mainWindow);
          }
        },
        { type: 'separator' },
        {
          label: '📂 Open Local PC Database Folder',
          click: () => {
            shell.openPath(dbDir);
          }
        },
        { type: 'separator' },
        { role: 'quit', label: 'Exit Jewellery ERP' }
      ]
    },
    {
      label: 'Edit',
      submenu: [
        { role: 'undo' },
        { role: 'redo' },
        { type: 'separator' },
        { role: 'cut' },
        { role: 'copy' },
        { role: 'paste' },
        { role: 'selectAll' }
      ]
    },
    {
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
    },
    {
      label: 'Help',
      submenu: [
        {
          label: 'About Jewellery ERP',
          click: () => {
            dialog.showMessageBox(mainWindow, {
              type: 'info',
              title: 'Jewellery ERP Desktop',
              message: 'Jewellery ERP - Offline Edition v1.0\nSaideep Jewellers\n\n100% Offline Standalone PC Application\nEmbedded SQLite Database with USB Pendrive Sync.'
            });
          }
        }
      ]
    }
  ];

  const menu = Menu.buildFromTemplate(template);
  Menu.setApplicationMenu(menu);
}

/**
 * Create Single Desktop Window
 */
function createWindow() {
  if (mainWindow) {
    if (mainWindow.isMinimized()) mainWindow.restore();
    mainWindow.focus();
    return;
  }

  if (isStartingWindow) return;
  isStartingWindow = true;

  mainWindow = new BrowserWindow({
    width: 1400,
    height: 900,
    minWidth: 1024,
    minHeight: 700,
    title: 'Jewellery ERP - Saideep Jewellers (Offline Edition)',
    icon: path.join(__dirname, 'assets/icon.png'),
    backgroundColor: '#0f172a',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: false
    }
  });

  // Enforce consistent title, preventing HTML page title overwrite
  mainWindow.on('page-title-updated', (e) => e.preventDefault());

  createMenu();

  const indexPath = path.join(frontendDist, 'index.html');
  if (fs.existsSync(indexPath)) {
    mainWindow.loadFile(indexPath);
  } else {
    mainWindow.loadURL('http://localhost:5174');
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
    isStartingWindow = false;
  });

  isStartingWindow = false;
}

/**
 * Terminate backend process cleanly
 */
function killBackend() {
  if (pythonProcess && pythonProcess.pid) {
    console.log(`[Desktop] Terminating backend PID ${pythonProcess.pid}...`);
    try {
      if (process.platform === 'win32') {
        exec(`taskkill /pid ${pythonProcess.pid} /T /F`, () => {});
      } else {
        pythonProcess.kill('SIGTERM');
      }
    } catch (e) {}
    pythonProcess = null;
  }
}

// IPC Handlers
ipcMain.on('get-backend-url', (event) => {
  event.returnValue = BACKEND_URL;
});

ipcMain.handle('get-database-path', () => dbPath);
ipcMain.handle('open-database-folder', () => {
  shell.openPath(dbDir);
  return true;
});

ipcMain.handle('backup-database', async () => {
  if (!mainWindow) return { success: false };
  const { filePath } = await dialog.showSaveDialog(mainWindow, {
    title: 'Backup Jewellery ERP Database',
    defaultPath: `jewellery_erp_backup_${new Date().toISOString().slice(0, 10)}.db`,
    filters: [{ name: 'SQLite Database', extensions: ['db', 'sqlite'] }]
  });
  if (filePath && fs.existsSync(dbPath)) {
    fs.copyFileSync(dbPath, filePath);
    return { success: true, path: filePath };
  }
  return { success: false };
});

ipcMain.handle('backup-to-usb', async () => {
  if (!mainWindow) return { success: false };
  return await backupToUsb(mainWindow);
});

ipcMain.handle('restore-database', async () => {
  if (!mainWindow) return { success: false };
  return await restoreDatabase(mainWindow);
});

ipcMain.handle('open-external', (_, url) => {
  shell.openExternal(url);
});

// App Lifecycle
app.whenReady().then(() => {
  startBackend();
  waitForBackend((err) => {
    if (err) {
      console.warn('[Desktop] Backend initialization warning:', err.message);
    }
    createWindow();
  });
});

app.on('second-instance', () => {
  if (mainWindow) {
    if (mainWindow.isMinimized()) mainWindow.restore();
    mainWindow.focus();
  }
});

app.on('activate', () => {
  if (BrowserWindow.getAllWindows().length === 0) {
    createWindow();
  }
});

app.on('will-quit', () => {
  killBackend();
});

app.on('window-all-closed', () => {
  killBackend();
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
