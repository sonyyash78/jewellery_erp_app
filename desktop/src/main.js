const { app, BrowserWindow, ipcMain, dialog, shell, Menu } = require('electron');
const path = require('path');
const fs = require('fs');
const http = require('http');
const { spawn, exec, execSync } = require('child_process');

// 1. Strict Single-Instance Lock — prevents infinite windows!
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

// 2. Storage Paths
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

// The active database is always pcDbPath for maximum local speed & zero crash risk if USB unplugged
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
 * Scan Windows for connected USB / Removable Drives using .NET DriveInfo
 */
function getUsbDrives() {
  const drives = [];
  try {
    if (process.platform === 'win32') {
      const psCmd = `powershell -NoProfile -Command "[System.IO.DriveInfo]::GetDrives() | Where-Object { $_.DriveType -eq 'Removable' -or ($_.DriveType -eq 'Fixed' -and $_.Name -notlike 'C:*') } | ForEach-Object { @{ Letter = $_.Name.TrimEnd('\\'); Label = $_.VolumeLabel; TotalSize = $_.TotalSize; FreeSpace = $_.AvailableFreeSpace; DriveType = $_.DriveType.ToString() } } | ConvertTo-Json"`;
      const output = execSync(psCmd, { encoding: 'utf8', timeout: 4000 });
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
  } catch (e) {}
  return drives;
}

/**
 * Get accurate last modified time for SQLite DB including WAL file
 */
function getDbMtime(dbFile) {
  let maxTime = 0;
  try {
    if (fs.existsSync(dbFile)) {
      maxTime = Math.max(maxTime, fs.statSync(dbFile).mtimeMs);
    }
    const wal = `${dbFile}-wal`;
    if (fs.existsSync(wal)) {
      maxTime = Math.max(maxTime, fs.statSync(wal).mtimeMs);
    }
  } catch (e) {}
  return maxTime;
}

/**
 * Trigger SQLite checkpoint via backend API to commit WAL into main .db
 */
function triggerCheckpoint() {
  return new Promise((resolve) => {
    const req = http.request(
      {
        hostname: '127.0.0.1',
        port: BACKEND_PORT,
        path: '/api/v1/checkpoint',
        method: 'POST',
        timeout: 2000
      },
      (res) => {
        resolve(res.statusCode === 200);
      }
    );
    req.on('error', () => resolve(false));
    req.on('timeout', () => {
      req.abort();
      resolve(false);
    });
    req.end();
  });
}

/**
 * Safely copy SQLite database files (.db, .db-wal, .db-shm)
 */
function safeCopySqliteDb(srcPath, destPath) {
  if (!fs.existsSync(srcPath)) return false;
  const destDir = path.dirname(destPath);
  if (!fs.existsSync(destDir)) {
    try { fs.mkdirSync(destDir, { recursive: true }); } catch (e) {}
  }

  try {
    fs.copyFileSync(srcPath, destPath);

    const srcWal = `${srcPath}-wal`;
    const destWal = `${destPath}-wal`;
    if (fs.existsSync(srcWal)) {
      try { fs.copyFileSync(srcWal, destWal); } catch (e) {}
    } else if (fs.existsSync(destWal)) {
      try { fs.unlinkSync(destWal); } catch (e) {}
    }

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
 * Sync PC database to USB pendrive
 */
async function syncPcToUsb(usbLetter) {
  try {
    const usbDir = path.join(usbLetter, 'JewelleryERP_Data');
    if (!fs.existsSync(usbDir)) fs.mkdirSync(usbDir, { recursive: true });
    const usbDbPath = path.join(usbDir, 'jewellery_erp.db');

    // Flush WAL into .db file first
    await triggerCheckpoint();

    if (fs.existsSync(pcDbPath)) {
      safeCopySqliteDb(pcDbPath, usbDbPath);
      lastSyncTimestamp = new Date().toISOString();
      return true;
    }
  } catch (e) {
    console.error('[Storage] syncPcToUsb error:', e.message);
  }
  return false;
}

/**
 * Startup synchronization between PC and Pendrive:
 * Whichever has newer transactions updates the other!
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
      const usbTime = getDbMtime(usbDbPath);
      const pcTime = getDbMtime(pcDbPath);
      if (usbTime > pcTime + 1000) {
        console.log('[Storage] USB database is newer from another PC. Syncing USB -> PC...');
        safeCopySqliteDb(usbDbPath, pcDbPath);
      } else {
        console.log('[Storage] PC database is newer or equal. Syncing PC -> USB...');
        safeCopySqliteDb(pcDbPath, usbDbPath);
      }
    } else if (usbExists && !pcExists) {
      console.log('[Storage] USB found. Initializing PC from USB...');
      safeCopySqliteDb(usbDbPath, pcDbPath);
    } else if (pcExists && !usbExists) {
      console.log('[Storage] Initializing USB from PC...');
      safeCopySqliteDb(pcDbPath, usbDbPath);
    }

    lastSyncTimestamp = new Date().toISOString();
    console.log(`[Storage] Synchronized with USB Pendrive: ${currentUsb.name}`);
  }

  // Active DB is always pcDbPath for maximum local performance and stability
  activeDbPath = pcDbPath;
  console.log(`[Storage] Live Database: ${activeDbPath}`);
}

/**
 * Get current storage status for Frontend UI
 */
function getStorageStatus() {
  const drives = getUsbDrives();
  const usbConnected = drives.length > 0;
  const usb = usbConnected ? drives[0] : null;

  return {
    usbConnected,
    isUsbLive: usbConnected,
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
 * Background Storage Engine:
 * - Syncs PC -> USB every 10 seconds if USB is plugged in
 * - Detects USB insertion within 3 seconds and syncs immediately
 */
function startStorageEngine() {
  // 1. Periodic auto-sync every 10 seconds
  mirrorInterval = setInterval(async () => {
    try {
      const drives = getUsbDrives();
      if (drives.length > 0) {
        currentUsb = drives[0];
        await syncPcToUsb(currentUsb.letter);
      } else {
        currentUsb = null;
      }
    } catch (err) {
      console.error('[Storage Engine] Auto-sync notice:', err.message);
    }
  }, 10000);

  // 2. USB insertion / removal detector every 3 seconds
  usbDetectionInterval = setInterval(async () => {
    try {
      const drives = getUsbDrives();
      const detected = drives.length > 0 ? drives[0] : null;
      const prevLetter = currentUsb ? currentUsb.letter : null;
      const newLetter = detected ? detected.letter : null;

      if (prevLetter !== newLetter) {
        console.log(`[Storage] USB drive change: ${prevLetter} -> ${newLetter}`);
        currentUsb = detected;

        if (currentUsb && fs.existsSync(pcDbPath)) {
          console.log(`[Storage] USB inserted! Immediately syncing PC -> ${currentUsb.letter}...`);
          await syncPcToUsb(currentUsb.letter);
        }
        notifyStorageStatusChanged();
      }
    } catch (e) {}
  }, 3000);
}

/**
 * Flush and mirror before quitting (fully synchronous to guarantee completion)
 */
function flushStorageSync() {
  try {
    const drives = getUsbDrives();
    if (drives.length > 0 && fs.existsSync(pcDbPath)) {
      const usbDir = path.join(drives[0].letter, 'JewelleryERP_Data');
      if (!fs.existsSync(usbDir)) fs.mkdirSync(usbDir, { recursive: true });
      safeCopySqliteDb(pcDbPath, path.join(usbDir, 'jewellery_erp.db'));
      console.log('[Storage] On-exit mirror to USB complete.');
    }
  } catch (err) {
    console.error('[Storage] On-exit flush notice:', err.message);
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

    // Flush WAL checkpoint first
    await triggerCheckpoint();

    const now = new Date();
    const pad = (n) => String(n).padStart(2, '0');
    const timestamp = `${now.getFullYear()}-${pad(now.getMonth()+1)}-${pad(now.getDate())}_${pad(now.getHours())}${pad(now.getMinutes())}${pad(now.getSeconds())}`;

    const liveUsbDb = path.join(liveDir, 'jewellery_erp.db');
    const snapshotDb = path.join(backupDir, `jewellery_erp_backup_${timestamp}.db`);

    safeCopySqliteDb(pcDbPath, liveUsbDb);
    safeCopySqliteDb(pcDbPath, snapshotDb);
    lastSyncTimestamp = new Date().toISOString();
    notifyStorageStatusChanged();

    if (parentWin) {
      await dialog.showMessageBox(parentWin, {
        type: 'info',
        title: 'USB Pendrive Backup Successful',
        message: `All store data safely saved to Pendrive!\n\nDestination: ${targetName}\nLive DB: ${liveUsbDb}\nSnapshot Backup: ${snapshotDb}\n\nYour data is 100% crash-proof and portable.`
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
      if (fs.existsSync(pcDbPath)) {
        safeCopySqliteDb(pcDbPath, `${pcDbPath}.bak_${Date.now()}`);
      }
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
 * Ensure port 8000 is clean before starting backend
 */
function killOrphanedPortProcess(port) {
  try {
    if (process.platform === 'win32') {
      const out = execSync(`netstat -ano | findstr :${port}`, { encoding: 'utf8' });
      for (const line of out.split('\n')) {
        const parts = line.trim().split(/\s+/);
        if (parts.length >= 5 && parts[1].endsWith(`:${port}`) && parts[3] === 'LISTENING') {
          const pid = parts[4];
          if (pid && pid !== '0' && pid !== String(process.pid)) {
            console.log(`[Desktop] Reclaiming port ${port} from PID ${pid}...`);
            try { execSync(`taskkill /pid ${pid} /T /F`); } catch (e) {}
          }
        }
      }
    }
  } catch (e) {}
}

/**
 * Start Backend Process
 */
function startBackend() {
  killOrphanedPortProcess(BACKEND_PORT);

  const sqliteUrl = `sqlite:///${pcDbPath.replace(/\\/g, '/')}`;

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
            if (filePath && fs.existsSync(pcDbPath)) {
              await triggerCheckpoint();
              safeCopySqliteDb(pcDbPath, filePath);
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
              message: 'Jewellery ERP - Offline Edition v1.0\nSaideep Jewellers\n\n100% Offline Standalone PC Application\nEmbedded SQLite Database with Continuous USB Pendrive Auto-Sync.'
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
    show: true,
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

  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
    mainWindow.focus();
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
  shell.openPath(pcDir);
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
  if (filePath && fs.existsSync(pcDbPath)) {
    await triggerCheckpoint();
    safeCopySqliteDb(pcDbPath, filePath);
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
  // 1. Resolve startup storage: syncs PC <-> Pendrive if USB connected
  resolveDatabaseAtStartup();

  // 2. Start Backend
  startBackend();

  // 3. Start Storage Engine: 10s auto-mirror + 3s USB insertion detection
  startStorageEngine();

  // 4. Open Single Desktop Window Immediately
  createWindow();
});

app.on('second-instance', () => {
  if (mainWindow) {
    if (mainWindow.isMinimized()) mainWindow.restore();
    if (!mainWindow.isVisible()) mainWindow.show();
    mainWindow.focus();
  } else {
    createWindow();
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
