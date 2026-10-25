const { app, BrowserWindow, ipcMain, dialog, shell, Menu } = require('electron');
const path = require('path');
const fs = require('fs');
const http = require('http');
const { spawn, exec, execSync } = require('child_process');

// 1. Strict Single-Instance Lock — prevents multiple windows spawning
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

// 2. Prepare Storage Paths
// PC Primary Storage: C:\Users\<Username>\JewelleryERP_Data
const pcDir = path.join(app.getPath('home'), 'JewelleryERP_Data');
try {
  if (!fs.existsSync(pcDir)) {
    fs.mkdirSync(pcDir, { recursive: true });
  }
} catch (e) {
  console.error('[Storage] Error creating PC directory:', e.message);
}
const pcDbPath = path.join(pcDir, 'jewellery_erp.db');

let activeDbPath = pcDbPath;
let currentUsb = null;
let lastSyncTimestamp = null;
let mirrorInterval = null;
let usbDetectionInterval = null;

// Paths for Standalone Backend & Frontend
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
 * Scan Windows for connected USB / Removable Drives using standard .NET DriveInfo
 */
function getUsbDrives() {
  const drives = [];
  try {
    if (process.platform === 'win32') {
      const psCmd = `powershell -NoProfile -Command "[System.IO.DriveInfo]::GetDrives() | Where-Object { $_.DriveType -eq 'Removable' -or ($_.DriveType -eq 'Fixed' -and $_.Name -notlike 'C:*') } | ForEach-Object { @{ Letter = $_.Name.TrimEnd('\\'); Label = $_.VolumeLabel; TotalSize = $_.TotalSize; FreeSpace = $_.AvailableFreeSpace; DriveType = $_.DriveType.ToString() } } | ConvertTo-Json"`;
      const output = execSync(psCmd, { encoding: 'utf8', timeout: 5000 });
      if (output && output.trim()) {
        const parsed = JSON.parse(output.trim());
        const list = Array.isArray(parsed) ? parsed : [parsed];
        for (const item of list) {
          if (item && item.Letter) {
            drives.push({
              letter: item.Letter,
              name: item.Label ? `${item.Letter} (${item.Label})` : `${item.Letter} (USB Pendrive)`,
              freeSpace: item.FreeSpace,
              driveType: item.DriveType
            });
          }
        }
      }
    }
  } catch (e) {
    // Non-fatal notice during background poll
  }
  return drives;
}

/**
 * Safely copy SQLite database along with WAL (-wal) and Shared Memory (-shm) files
 */
function safeCopySqliteDb(srcPath, destPath) {
  if (!fs.existsSync(srcPath)) return false;
  const destDir = path.dirname(destPath);
  if (!fs.existsSync(destDir)) {
    try { fs.mkdirSync(destDir, { recursive: true }); } catch (e) {}
  }

  try {
    // 1. Copy main database
    fs.copyFileSync(srcPath, destPath);

    // 2. Copy -wal if exists
    const srcWal = `${srcPath}-wal`;
    const destWal = `${destPath}-wal`;
    if (fs.existsSync(srcWal)) {
      try { fs.copyFileSync(srcWal, destWal); } catch (e) {}
    } else if (fs.existsSync(destWal)) {
      try { fs.unlinkSync(destWal); } catch (e) {}
    }

    // 3. Copy -shm if exists
    const srcShm = `${srcPath}-shm`;
    const destShm = `${destPath}-shm`;
    if (fs.existsSync(srcShm)) {
      try { fs.copyFileSync(srcShm, destShm); } catch (e) {}
    } else if (fs.existsSync(destShm)) {
      try { fs.unlinkSync(destShm); } catch (e) {}
    }
    return true;
  } catch (err) {
    console.error(`[Storage] safeCopySqliteDb error: ${err.message}`);
    return false;
  }
}

/**
 * Startup Database Resolution:
 * If a USB Pendrive is connected:
 * 1. Synchronize USB and PC (whichever has the newer database updates the older one).
 * 2. Set ACTIVE DB directly on the Pendrive (all SQL writes commit to USB in real-time!).
 * If no USB is connected:
 * Active DB is PC, and background detector will auto-mirror when USB is inserted.
 */
function resolveDatabaseAtStartup() {
  const usbDrives = getUsbDrives();
  if (usbDrives.length > 0) {
    currentUsb = usbDrives[0];
    const usbDir = path.join(currentUsb.letter, 'JewelleryERP_Data');
    if (!fs.existsSync(usbDir)) {
      try { fs.mkdirSync(usbDir, { recursive: true }); } catch (e) {}
    }
    const usbDbPath = path.join(usbDir, 'jewellery_erp.db');

    const pcExists = fs.existsSync(pcDbPath);
    const usbExists = fs.existsSync(usbDbPath);

    if (usbExists && pcExists) {
      try {
        const usbMtime = fs.statSync(usbDbPath).mtimeMs;
        const pcMtime = fs.statSync(pcDbPath).mtimeMs;
        if (usbMtime >= pcMtime) {
          console.log('[Storage] USB database is newer. Mirroring USB -> PC...');
          safeCopySqliteDb(usbDbPath, pcDbPath);
        } else {
          console.log('[Storage] PC database is newer. Mirroring PC -> USB...');
          safeCopySqliteDb(pcDbPath, usbDbPath);
        }
      } catch (e) {
        console.error('[Storage] Timestamp check notice:', e.message);
      }
    } else if (usbExists && !pcExists) {
      console.log('[Storage] USB DB found. Mirroring to PC...');
      safeCopySqliteDb(usbDbPath, pcDbPath);
    } else if (pcExists && !usbExists) {
      console.log('[Storage] Initializing USB database from PC...');
      safeCopySqliteDb(pcDbPath, usbDbPath);
    }

    // Set ACTIVE DB to USB!
    activeDbPath = usbDbPath;
    lastSyncTimestamp = new Date().toISOString();
    console.log(`[Storage] PRIMARY LIVE DATABASE ACTIVATED ON USB: ${activeDbPath}`);
  } else {
    activeDbPath = pcDbPath;
    console.log(`[Storage] PRIMARY LIVE DATABASE ACTIVATED ON PC: ${activeDbPath}`);
  }
}

/**
 * Returns storage state for frontend UI
 */
function getStorageStatus() {
  const drives = getUsbDrives();
  const usbConnected = drives.length > 0;
  const usb = usbConnected ? drives[0] : null;
  const isUsbLive = Boolean(usb && activeDbPath.startsWith(usb.letter));

  return {
    isUsbLive,
    usbConnected,
    usbLetter: usb ? usb.letter : null,
    usbName: usb ? usb.name : null,
    activePath: activeDbPath,
    pcPath: pcDbPath,
    usbPath: usb ? path.join(usb.letter, 'JewelleryERP_Data', 'jewellery_erp.db') : null,
    lastSyncTimestamp
  };
}

function notifyStorageStatusChanged() {
  if (mainWindow && !mainWindow.isDestroyed()) {
    mainWindow.webContents.send('storage-status-changed', getStorageStatus());
  }
}

/**
 * Start real-time background mirroring and USB insertion watcher
 */
function startStorageEngine() {
  // 1. Periodic Mirror Interval (Every 20 seconds)
  mirrorInterval = setInterval(() => {
    try {
      const drives = getUsbDrives();
      if (drives.length > 0) {
        const usb = drives[0];
        const usbDir = path.join(usb.letter, 'JewelleryERP_Data');
        const usbDbPath = path.join(usbDir, 'jewellery_erp.db');

        if (activeDbPath.startsWith(usb.letter)) {
          // Live on USB -> Mirror to PC
          if (fs.existsSync(activeDbPath)) {
            safeCopySqliteDb(activeDbPath, pcDbPath);
            lastSyncTimestamp = new Date().toISOString();
          }
        } else {
          // Live on PC -> Mirror to USB
          if (fs.existsSync(pcDbPath)) {
            if (!fs.existsSync(usbDir)) fs.mkdirSync(usbDir, { recursive: true });
            safeCopySqliteDb(pcDbPath, usbDbPath);
            lastSyncTimestamp = new Date().toISOString();
          }
        }
      }
    } catch (err) {
      console.error('[Storage Engine] Mirror error:', err.message);
    }
  }, 20000);

  // 2. USB Insertion / Removal Watcher (Every 4 seconds)
  usbDetectionInterval = setInterval(() => {
    try {
      const drives = getUsbDrives();
      const detected = drives.length > 0 ? drives[0] : null;
      const prevLetter = currentUsb ? currentUsb.letter : null;
      const newLetter = detected ? detected.letter : null;

      if (prevLetter !== newLetter) {
        console.log(`[Storage] USB drive change: ${prevLetter} -> ${newLetter}`);
        currentUsb = detected;

        if (currentUsb && !activeDbPath.startsWith(currentUsb.letter) && fs.existsSync(pcDbPath)) {
          // USB was inserted while running on PC — auto-mirror to USB immediately!
          const usbDir = path.join(currentUsb.letter, 'JewelleryERP_Data');
          if (!fs.existsSync(usbDir)) fs.mkdirSync(usbDir, { recursive: true });
          const usbDbPath = path.join(usbDir, 'jewellery_erp.db');
          safeCopySqliteDb(pcDbPath, usbDbPath);
          lastSyncTimestamp = new Date().toISOString();
          console.log(`[Storage] Auto-mirrored to newly connected USB: ${usbDbPath}`);
        }
        notifyStorageStatusChanged();
      }
    } catch (e) {}
  }, 4000);
}

/**
 * Flush and mirror before exiting
 */
function flushStorageSync() {
  try {
    const drives = getUsbDrives();
    if (drives.length > 0) {
      const usb = drives[0];
      const usbDir = path.join(usb.letter, 'JewelleryERP_Data');
      const usbDbPath = path.join(usbDir, 'jewellery_erp.db');

      if (activeDbPath.startsWith(usb.letter) && fs.existsSync(activeDbPath)) {
        safeCopySqliteDb(activeDbPath, pcDbPath);
        console.log('[Storage] On-exit mirror USB -> PC complete.');
      } else if (fs.existsSync(pcDbPath)) {
        if (!fs.existsSync(usbDir)) fs.mkdirSync(usbDir, { recursive: true });
        safeCopySqliteDb(pcDbPath, usbDbPath);
        console.log('[Storage] On-exit mirror PC -> USB complete.');
      }
    }
  } catch (err) {
    console.error('[Storage] On-exit flush error:', err.message);
  }
}

/**
 * 1-Click Backup / Sync to Pendrive
 */
async function backupToUsb(parentWin) {
  try {
    const drives = getUsbDrives();
    let targetLetter = null;
    let targetName = '';

    if (drives.length === 1) {
      targetLetter = drives[0].letter;
      targetName = drives[0].name;
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
        targetLetter = drives[res.response].letter;
        targetName = drives[res.response].name;
      } else {
        return { success: false, cancelled: true };
      }
    } else {
      const res = await dialog.showOpenDialog(parentWin, {
        title: 'Select USB Pendrive or Backup Folder',
        properties: ['openDirectory', 'createDirectory']
      });
      if (!res.canceled && res.filePaths.length > 0) {
        targetLetter = res.filePaths[0];
        targetName = res.filePaths[0];
      } else {
        return { success: false, cancelled: true };
      }
    }

    const liveDir = path.join(targetLetter, 'JewelleryERP_Data');
    const backupDir = path.join(targetLetter, 'JewelleryERP_Backups');
    if (!fs.existsSync(liveDir)) fs.mkdirSync(liveDir, { recursive: true });
    if (!fs.existsSync(backupDir)) fs.mkdirSync(backupDir, { recursive: true });

    const now = new Date();
    const pad = (n) => String(n).padStart(2, '0');
    const timestamp = `${now.getFullYear()}-${pad(now.getMonth()+1)}-${pad(now.getDate())}_${pad(now.getHours())}${pad(now.getMinutes())}${pad(now.getSeconds())}`;

    const liveUsbDb = path.join(liveDir, 'jewellery_erp.db');
    const snapshotDb = path.join(backupDir, `jewellery_erp_backup_${timestamp}.db`);

    const src = fs.existsSync(activeDbPath) ? activeDbPath : pcDbPath;
    safeCopySqliteDb(src, liveUsbDb);
    safeCopySqliteDb(src, snapshotDb);
    lastSyncTimestamp = new Date().toISOString();
    notifyStorageStatusChanged();

    if (parentWin) {
      await dialog.showMessageBox(parentWin, {
        type: 'info',
        title: 'USB Pendrive Backup Successful',
        message: `All store data safely saved to Pendrive!\n\nDrive / Folder: ${targetName}\nLive File: ${liveUsbDb}\nSnapshot File: ${snapshotDb}\n\nYour data is 100% safe and portable.`
      });
    }

    return {
      success: true,
      usbName: targetName,
      livePath: liveUsbDb,
      snapshotPath: snapshotDb,
      timestamp
    };
  } catch (err) {
    if (parentWin) {
      dialog.showErrorBox('Backup Error', `Failed to copy database: ${err.message}`);
    }
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
      if (fs.existsSync(activeDbPath)) {
        safeCopySqliteDb(activeDbPath, `${activeDbPath}.bak_${Date.now()}`);
      }
      safeCopySqliteDb(selectedFile, activeDbPath);
      safeCopySqliteDb(selectedFile, pcDbPath);

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
 * Start Backend Process
 */
function startBackend() {
  // Convert Windows path to SQLAlchemy SQLite format (sqlite:///E:/JewelleryERP_Data/jewellery_erp.db)
  const sqliteUrl = `sqlite:///${activeDbPath.replace(/\\/g, '/')}`;

  const env = {
    ...process.env,
    PYTHONUNBUFFERED: '1',
    DATABASE_URL: sqliteUrl,
    OFFLINE_MODE: 'true',
    ENVIRONMENT: 'offline',
    SECRET_KEY: 'jewellery-erp-desktop-offline-secret-key-2026',
    INITIAL_ADMIN_PASSWORD: 'admin',
    BACKEND_PORT: String(BACKEND_PORT),
    BACKEND_HOST: '127.0.0.1'
  };

  console.log(`[Desktop] Starting Backend with DATABASE_URL=${sqliteUrl}`);

  if (fs.existsSync(standaloneBinary)) {
    console.log(`[Desktop] Spawning Standalone Backend: ${standaloneBinary}`);
    pythonProcess = spawn(standaloneBinary, [], {
      cwd: path.dirname(standaloneBinary),
      env,
      stdio: ['ignore', 'pipe', 'pipe']
    });
  } else {
    const pythonCmd = process.platform === 'win32' ? 'python' : 'python3';
    const scriptPath = path.join(backendDir, 'run_server.py');
    console.log(`[Desktop] Spawning Python interpreter: ${scriptPath}`);
    pythonProcess = spawn(pythonCmd, [scriptPath], {
      cwd: backendDir,
      env,
      stdio: ['ignore', 'pipe', 'pipe']
    });
  }

  pythonProcess.stdout.on('data', (d) => console.log(`[Backend] ${d.toString().trim()}`));
  pythonProcess.stderr.on('data', (d) => console.error(`[Backend] ${d.toString().trim()}`));
  pythonProcess.on('exit', (code, signal) => {
    console.log(`[Desktop] Backend process exited (code=${code}, signal=${signal})`);
  });
}

/**
 * Poll Backend until ready
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
 * Menu bar
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
          label: '🔄 Sync Now (PC <-> Pendrive)',
          accelerator: 'CmdOrCtrl+S',
          click: () => {
            if (mainWindow) backupToUsb(mainWindow);
          }
        },
        {
          label: '💾 Save Backup Database As...',
          accelerator: 'CmdOrCtrl+B',
          click: async () => {
            const { filePath } = await dialog.showSaveDialog(mainWindow, {
              title: 'Backup Jewellery ERP Database',
              defaultPath: `jewellery_erp_backup_${new Date().toISOString().slice(0, 10)}.db`,
              filters: [{ name: 'SQLite Database', extensions: ['db', 'sqlite'] }]
            });
            if (filePath && fs.existsSync(activeDbPath)) {
              safeCopySqliteDb(activeDbPath, filePath);
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
          label: '📂 Open Active Database Folder',
          click: () => {
            shell.openPath(path.dirname(activeDbPath));
          }
        },
        {
          label: '📂 Open PC Storage Folder',
          click: () => {
            shell.openPath(pcDir);
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
              message: 'Jewellery ERP - Offline Edition v1.0\nSaideep Jewellers\n\n100% Offline Standalone PC Application\nEmbedded SQLite Database with Real-time USB Pendrive Storage Engine.'
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

ipcMain.handle('get-database-path', () => activeDbPath);
ipcMain.handle('get-storage-status', () => getStorageStatus());

ipcMain.handle('open-database-folder', () => {
  shell.openPath(path.dirname(activeDbPath));
  return true;
});

ipcMain.handle('sync-now', async () => {
  if (!mainWindow) return { success: false };
  return await backupToUsb(mainWindow);
});

ipcMain.handle('backup-database', async () => {
  if (!mainWindow) return { success: false };
  const { filePath } = await dialog.showSaveDialog(mainWindow, {
    title: 'Backup Jewellery ERP Database',
    defaultPath: `jewellery_erp_backup_${new Date().toISOString().slice(0, 10)}.db`,
    filters: [{ name: 'SQLite Database', extensions: ['db', 'sqlite'] }]
  });
  if (filePath && fs.existsSync(activeDbPath)) {
    safeCopySqliteDb(activeDbPath, filePath);
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
  // 1. Resolve startup storage: Pendrive if connected, else PC
  resolveDatabaseAtStartup();

  // 2. Start Standalone Backend
  startBackend();

  // 3. Start Real-time Mirroring & USB Watcher
  startStorageEngine();

  // 4. Wait for backend readiness then show window
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
  if (mirrorInterval) clearInterval(mirrorInterval);
  if (usbDetectionInterval) clearInterval(usbDetectionInterval);
  flushStorageSync();
  killBackend();
});

app.on('window-all-closed', () => {
  if (mirrorInterval) clearInterval(mirrorInterval);
  if (usbDetectionInterval) clearInterval(usbDetectionInterval);
  flushStorageSync();
  killBackend();
  if (process.platform !== 'darwin') {
    app.quit();
  }
});
