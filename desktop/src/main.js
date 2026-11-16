const { app, BrowserWindow, ipcMain, dialog, shell, Menu } = require('electron');

const path = require('path');

const fs = require('fs');

const http = require('http');

const { spawn, exec, execFile, execSync } = require('child_process');



// 1. Strict Single-Instance Lock — prevents infinite windows!

// Native OS print dialog is used instead of Chromium's --enable-print-preview,
// which freezes Electron renderer processes (no chrome://print WebUI in Electron).



const gotTheLock = app.requestSingleInstanceLock();

if (!gotTheLock) {

  console.log('[Desktop] Another instance is already running. Quitting.');

  app.quit();

  process.exit(0);

}



let mainWindow = null;

let pythonProcess = null;

let isStartingWindow = false;
let isAppQuitting = false;
let pdfBridgeServer = null;
let pdfBridgeUrl = '';



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

const desktopLogFile = path.join(pcDir, 'desktop_debug.log');
const origLog = console.log;
const origErr = console.error;
console.log = (...args) => {
  try { fs.appendFileSync(desktopLogFile, `[LOG ${new Date().toISOString()}] ${args.join(' ')}\n`); } catch (e) {}
  origLog.apply(console, args);
};
console.error = (...args) => {
  try { fs.appendFileSync(desktopLogFile, `[ERR ${new Date().toISOString()}] ${args.join(' ')}\n`); } catch (e) {}
  origErr.apply(console, args);
};




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



const USB_SCAN_PS_CMD = `[System.IO.DriveInfo]::GetDrives() | Where-Object { $_.DriveType -eq 'Removable' -or ($_.DriveType -eq 'Fixed' -and $_.Name -notlike 'C:*') } | ForEach-Object { @{ Letter = $_.Name.TrimEnd('\\'); Label = $_.VolumeLabel; TotalSize = $_.TotalSize; FreeSpace = $_.AvailableFreeSpace; DriveType = $_.DriveType.ToString() } } | ConvertTo-Json`;

let cachedUsbDrives = [];
let lastDriveScanAt = 0;
let driveScanPromise = null;
let isStorageSyncRunning = false;
let lastSyncedDbMtime = 0;
let lastSyncedArchiveSig = '';

function parseUsbDriveOutput(output) {
  const drives = [];
  if (!output || !output.trim()) return drives;
  try {
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
  } catch {}
  return drives;
}

/**
 * Synchronous drive scan used ONCE at startup before UI window creation.
 */
function scanUsbDrivesSyncOnce() {
  try {
    if (process.platform === 'win32') {
      const output = execSync(`powershell -NoProfile -NonInteractive -Command "${USB_SCAN_PS_CMD}"`, {
        encoding: 'utf8',
        timeout: 4000,
        windowsHide: true
      });
      cachedUsbDrives = parseUsbDriveOutput(output);
      lastDriveScanAt = Date.now();
    }
  } catch {}
  return cachedUsbDrives;
}

/**
 * Non-blocking async drive scan so UI rendering and IPC never freeze on PowerShell/WMI calls.
 */
function refreshUsbDrivesAsync(force = false) {
  if (process.platform !== 'win32') return Promise.resolve([]);
  if (!force && Date.now() - lastDriveScanAt < 8000) {
    return Promise.resolve(cachedUsbDrives);
  }
  if (driveScanPromise) return driveScanPromise;

  driveScanPromise = new Promise((resolve) => {
    execFile(
      'powershell.exe',
      ['-NoProfile', '-NonInteractive', '-Command', USB_SCAN_PS_CMD],
      { encoding: 'utf8', timeout: 4000, windowsHide: true },
      (err, stdout) => {
        if (!err && stdout) {
          cachedUsbDrives = parseUsbDriveOutput(stdout);
        } else if (!err) {
          cachedUsbDrives = [];
        }
        lastDriveScanAt = Date.now();
        driveScanPromise = null;
        resolve(cachedUsbDrives);
      }
    );
  });
  return driveScanPromise;
}

/**
 * Fast non-blocking cached accessor (never invokes execSync at runtime).
 */
function getUsbDrives() {
  return cachedUsbDrives;
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



/**
 * Helpers for consistent Vault sanitization, persistent backup roots, and external archive sync
 */
function sanitizeVaultName(name, fallback = 'Unknown') {
  const raw = String(name || '').trim();
  if (!raw) return fallback;
  if (/^walk[\s_-]*in(?:[\s_-]*customer)?s?$/i.test(raw)) {
    return 'Walkin_Customer';
  }
  return raw.replace(/[\\/*?:"<>|]/g, '_').replace(/\s+/g, '_').slice(0, 60);
}

function getStorageConfigPath() {
  return path.join(pcDir, 'storage_config.json');
}

function loadCustomBackupDirs() {
  try {
    const cfgPath = getStorageConfigPath();
    if (!fs.existsSync(cfgPath)) return [];
    const parsed = JSON.parse(fs.readFileSync(cfgPath, 'utf8'));
    return Array.isArray(parsed.customBackupDirs) ? parsed.customBackupDirs : [];
  } catch {
    return [];
  }
}

function rememberCustomBackupDir(dirPath) {
  if (!dirPath) return;
  try {
    const resolved = path.resolve(String(dirPath));
    const existing = loadCustomBackupDirs();
    const next = [resolved, ...existing.filter((d) => path.resolve(d).toLowerCase() !== resolved.toLowerCase())].slice(0, 5);
    if (!fs.existsSync(pcDir)) fs.mkdirSync(pcDir, { recursive: true });
    fs.writeFileSync(getStorageConfigPath(), JSON.stringify({ customBackupDirs: next }, null, 2), 'utf8');
  } catch {}
}

function getAllExternalArchiveDirs() {
  const pcArchiveResolved = path.resolve(path.join(pcDir, 'Archived_PDFs')).toLowerCase();
  const result = [];
  const seen = new Set([pcArchiveResolved]);

  const addCandidate = (candidateDir) => {
    try {
      const resolved = path.resolve(candidateDir);
      const key = resolved.toLowerCase();
      if (!seen.has(key)) {
        seen.add(key);
        result.push(resolved);
      }
    } catch {}
  };

  for (const d of getUsbDrives()) {
    addCandidate(path.join(d.letter, 'JewelleryERP_Data', 'Archived_PDFs'));
  }

  try {
    const downloadsBackup = path.join(app.getPath('downloads'), 'JewelleryERP_Backups');
    if (fs.existsSync(downloadsBackup)) {
      addCandidate(path.join(downloadsBackup, 'JewelleryERP_Data', 'Archived_PDFs'));
    }
  } catch {}

  for (const customDir of loadCustomBackupDirs()) {
    try {
      if (fs.existsSync(customDir)) {
        const base = path.basename(customDir).toLowerCase();
        const archiveDir = base === 'jewelleryerp_data'
          ? path.join(customDir, 'Archived_PDFs')
          : path.join(customDir, 'JewelleryERP_Data', 'Archived_PDFs');
        addCandidate(archiveDir);
      }
    } catch {}
  }

  return result;
}

async function getDirChangeSignatureAsync(dirPath) {
  let fileCount = 0;
  let maxMtime = 0;
  const walk = async (cur) => {
    let entries;
    try {
      entries = await fs.promises.readdir(cur, { withFileTypes: true });
    } catch {
      return;
    }
    for (const entry of entries) {
      const full = path.join(cur, entry.name);
      if (entry.isDirectory()) {
        await walk(full);
      } else if (entry.isFile()) {
        fileCount += 1;
        try {
          const st = await fs.promises.stat(full);
          if (st.mtimeMs > maxMtime) maxMtime = st.mtimeMs;
        } catch {}
      }
    }
  };
  await walk(dirPath);
  return `${fileCount}:${Math.round(maxMtime)}`;
}

async function syncDirectoryAsync(srcDir, destDir) {
  if (!fs.existsSync(srcDir)) return;
  try {
    await fs.promises.mkdir(destDir, { recursive: true });
  } catch {}

  try {
    const entries = await fs.promises.readdir(srcDir, { withFileTypes: true });
    const srcNames = new Set(entries.map((e) => e.name));

    try {
      const destEntries = await fs.promises.readdir(destDir, { withFileTypes: true });
      for (const dEntry of destEntries) {
        if (!srcNames.has(dEntry.name)) {
          await fs.promises.rm(path.join(destDir, dEntry.name), { recursive: true, force: true }).catch(() => {});
        }
      }
    } catch {}

    for (const entry of entries) {
      const srcPath = path.join(srcDir, entry.name);
      const destPath = path.join(destDir, entry.name);
      if (entry.isDirectory()) {
        await syncDirectoryAsync(srcPath, destPath);
      } else if (entry.isFile()) {
        let shouldCopy = false;
        try {
          const sStat = await fs.promises.stat(srcPath);
          try {
            const dStat = await fs.promises.stat(destPath);
            if (sStat.mtimeMs > dStat.mtimeMs + 1000 || sStat.size !== dStat.size) {
              shouldCopy = true;
            }
          } catch {
            shouldCopy = true;
          }
        } catch {}

        if (shouldCopy) {
          try {
            await fs.promises.copyFile(srcPath, destPath);
          } catch {}
        }
      }
    }
  } catch (err) {
    console.error(`[Storage] syncDirectoryAsync error: ${err.message}`);
  }
}

async function syncPcArchiveToExternalRootsAsync(extraAlreadySyncedDirs = []) {
  const pcArchiveDir = path.join(pcDir, 'Archived_PDFs');
  if (!fs.existsSync(pcArchiveDir)) return;
  const skipSet = new Set(extraAlreadySyncedDirs.map((d) => path.resolve(d).toLowerCase()));
  for (const targetArchiveDir of getAllExternalArchiveDirs()) {
    if (skipSet.has(path.resolve(targetArchiveDir).toLowerCase())) continue;
    try {
      await syncDirectoryAsync(pcArchiveDir, targetArchiveDir);
    } catch (e) {
      console.warn('[Archive Sync Error]', targetArchiveDir, e.message);
    }
  }
}

async function safeCopySqliteDbAsync(srcPath, destPath) {
  if (!fs.existsSync(srcPath)) return false;
  try {
    await fs.promises.mkdir(path.dirname(destPath), { recursive: true });
    await fs.promises.copyFile(srcPath, destPath);

    const srcWal = `${srcPath}-wal`;
    const destWal = `${destPath}-wal`;
    if (fs.existsSync(srcWal)) {
      await fs.promises.copyFile(srcWal, destWal).catch(() => {});
    } else if (fs.existsSync(destWal)) {
      await fs.promises.unlink(destWal).catch(() => {});
    }

    const srcShm = `${srcPath}-shm`;
    const destShm = `${destPath}-shm`;
    if (fs.existsSync(srcShm)) {
      await fs.promises.copyFile(srcShm, destShm).catch(() => {});
    } else if (fs.existsSync(destShm)) {
      await fs.promises.unlink(destShm).catch(() => {});
    }
    return true;
  } catch (err) {
    console.error(`[Storage] safeCopySqliteDbAsync error: ${err.message}`);
    return false;
  }
}

/**
 * Trigger backend to archive missing/updated bills, exchanges, purchases, and statements to PDF
 */
function triggerPdfArchive(options = {}) {
  return new Promise((resolve) => {
    const postData = JSON.stringify({
      force_refresh: Boolean(options && options.forceRefresh),
      refresh_statements: options && options.refreshStatements !== undefined ? Boolean(options.refreshStatements) : true,
    });
    const req = http.request(
      {
        hostname: '127.0.0.1',
        port: BACKEND_PORT,
        path: '/api/v1/archive-pdfs',
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Content-Length': Buffer.byteLength(postData),
        },
        timeout: 120000,
      },
      (res) => {
        res.resume();
        resolve(res.statusCode === 200);
      }
    );
    req.on('error', () => resolve(false));
    req.on('timeout', () => {
      req.destroy();
      resolve(false);
    });
    req.write(postData);
    req.end();
  });
}



/**

 * Recursively sync a directory, copying new and modified files

 */

function syncDirectory(srcDir, destDir) {

  if (!fs.existsSync(srcDir)) return;

  if (!fs.existsSync(destDir)) {

    try { fs.mkdirSync(destDir, { recursive: true }); } catch (e) {}

  }

  try {

    const entries = fs.readdirSync(srcDir, { withFileTypes: true });

    const srcNames = new Set(entries.map(e => e.name));



    // Remove obsolete files/folders in mirror that do not exist in source

    try {

      const destEntries = fs.readdirSync(destDir, { withFileTypes: true });

      for (const dEntry of destEntries) {

        if (!srcNames.has(dEntry.name)) {

          const obsoletePath = path.join(destDir, dEntry.name);

          fs.rmSync(obsoletePath, { recursive: true, force: true });

        }

      }

    } catch (e) {}

    for (const entry of entries) {

      const srcPath = path.join(srcDir, entry.name);

      const destPath = path.join(destDir, entry.name);

      if (entry.isDirectory()) {

        syncDirectory(srcPath, destPath);

      } else if (entry.isFile()) {

        let shouldCopy = false;

        if (!fs.existsSync(destPath)) {

          shouldCopy = true;

        } else {

          const sStat = fs.statSync(srcPath);

          const dStat = fs.statSync(destPath);

          if (sStat.mtimeMs > dStat.mtimeMs + 1000 || sStat.size !== dStat.size) {

            shouldCopy = true;

          }

        }

        if (shouldCopy) {

          try { fs.copyFileSync(srcPath, destPath); } catch (e) {}

        }

      }

    }

  } catch (err) {

    console.error(`[Storage] syncDirectory error: ${err.message}`);

  }

}



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

async function syncPcToUsb(usbLetter, force = false) {
  if (isStorageSyncRunning) return false;
  isStorageSyncRunning = true;
  try {
    const usbDir = path.join(usbLetter, 'JewelleryERP_Data');
    const usbDbPath = path.join(usbDir, 'jewellery_erp.db');
    const pcArchiveDir = path.join(pcDir, 'Archived_PDFs');
    const usbArchiveDir = path.join(usbDir, 'Archived_PDFs');

    const dbMtime = getDbMtime(pcDbPath);
    const archSig = fs.existsSync(pcArchiveDir) ? await getDirChangeSignatureAsync(pcArchiveDir) : 'none';
    const usbDbMissing = !fs.existsSync(usbDbPath);

    // Skip all checkpoint/IO churn if nothing changed since last background mirror
    if (!force && !usbDbMissing && dbMtime === lastSyncedDbMtime && archSig === lastSyncedArchiveSig) {
      return true;
    }

    await fs.promises.mkdir(usbDir, { recursive: true });
    await triggerCheckpoint();

    if (fs.existsSync(pcDbPath)) {
      await safeCopySqliteDbAsync(pcDbPath, usbDbPath);
      lastSyncedDbMtime = getDbMtime(pcDbPath);
    }

    if (fs.existsSync(pcArchiveDir)) {
      await syncDirectoryAsync(pcArchiveDir, usbArchiveDir);
      lastSyncedArchiveSig = archSig;
    }

    lastSyncTimestamp = new Date().toISOString();
    return true;
  } catch (e) {
    console.error('[Storage] syncPcToUsb error:', e.message);
    return false;
  } finally {
    isStorageSyncRunning = false;
  }
}

/**
 * Startup synchronization between PC and Pendrive:
 * Whichever has newer transactions updates the other!
 */
function resolveDatabaseAtStartup() {
  const usbDrives = scanUsbDrivesSyncOnce();

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
  // 1. Periodic non-blocking auto-mirror every 20 seconds when DB or PDFs changed
  mirrorInterval = setInterval(async () => {
    if (isStorageSyncRunning || isAppQuitting) return;
    try {
      const drives = await refreshUsbDrivesAsync(false);
      if (drives.length > 0) {
        currentUsb = drives[0];
        await syncPcToUsb(currentUsb.letter, false);
      } else {
        currentUsb = null;
      }
    } catch (err) {
      console.error('[Storage Engine] Auto-sync notice:', err.message);
    }
  }, 20000);

  // 2. Non-blocking USB insertion / removal detector every 8 seconds
  usbDetectionInterval = setInterval(async () => {
    if (isAppQuitting) return;
    try {
      const drives = await refreshUsbDrivesAsync(true);
      const detected = drives.length > 0 ? drives[0] : null;
      const prevLetter = currentUsb ? currentUsb.letter : null;
      const newLetter = detected ? detected.letter : null;

      if (prevLetter !== newLetter) {
        console.log(`[Storage] USB drive change: ${prevLetter} -> ${newLetter}`);
        currentUsb = detected;

        if (currentUsb && fs.existsSync(pcDbPath)) {
          console.log(`[Storage] USB inserted! Immediately syncing PC -> ${currentUsb.letter}...`);
          await syncPcToUsb(currentUsb.letter, true);
        }
        notifyStorageStatusChanged();
      }
    } catch {}
  }, 8000);
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

async function backupToUsb(parentWin, options = {}) {
  // Wait briefly if a background auto-sync cycle is mid-flight to avoid WinError 32 contention
  const lockWaitStart = Date.now();
  while (isStorageSyncRunning && Date.now() - lockWaitStart < 5000) {
    await new Promise((r) => setTimeout(r, 80));
  }
  isStorageSyncRunning = true;

  try {
    const drives = await refreshUsbDrivesAsync(true);
    let targetLetter = null;
    let targetName = '';
    let isCustomFolder = false;

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
      const defaultBackupDir = path.join(app.getPath('downloads'), 'JewelleryERP_Backups');
      const res = await dialog.showOpenDialog(parentWin, {
        title: 'Select USB Pendrive or Backup Folder',
        defaultPath: fs.existsSync(defaultBackupDir) ? defaultBackupDir : app.getPath('downloads'),
        properties: ['openDirectory', 'createDirectory']
      });
      if (!res.canceled && res.filePaths.length > 0) {
        targetLetter = res.filePaths[0];
        targetName = res.filePaths[0];
        isCustomFolder = true;
      } else {
        return { success: false, cancelled: true };
      }
    }

    const baseFolderName = path.basename(targetLetter).toLowerCase();
    const isDataDir = baseFolderName === 'jewelleryerp_data';
    const isBackupNamedDir = baseFolderName === 'jewelleryerp_backups';

    const liveDir = isDataDir ? targetLetter : path.join(targetLetter, 'JewelleryERP_Data');
    const backupDir = isBackupNamedDir
      ? targetLetter
      : (isDataDir ? path.join(path.dirname(targetLetter), 'JewelleryERP_Backups') : path.join(targetLetter, 'JewelleryERP_Backups'));

    await fs.promises.mkdir(liveDir, { recursive: true });
    await fs.promises.mkdir(backupDir, { recursive: true });

    if (isCustomFolder) {
      rememberCustomBackupDir(isDataDir ? path.dirname(targetLetter) : targetLetter);
    }

    // Flush WAL checkpoint first
    await triggerCheckpoint();

    const now = new Date();
    const pad = (n) => String(n).padStart(2, '0');
    const timestamp = `${now.getFullYear()}-${pad(now.getMonth() + 1)}-${pad(now.getDate())}_${pad(now.getHours())}${pad(now.getMinutes())}${pad(now.getSeconds())}`;

    const liveUsbDb = path.join(liveDir, 'jewellery_erp.db');
    const snapshotDb = path.join(backupDir, `jewellery_erp_backup_${timestamp}.db`);

    await safeCopySqliteDbAsync(pcDbPath, liveUsbDb);
    await safeCopySqliteDbAsync(pcDbPath, snapshotDb);

    // Generate/refresh PDFs unless caller already ran /backup/archive-pdfs in this action
    if (!options || !options.skipArchive) {
      await triggerPdfArchive({ forceRefresh: false, refreshStatements: true });
    }

    const pcArchiveDir = path.join(pcDir, 'Archived_PDFs');
    const usbArchiveDir = path.join(liveDir, 'Archived_PDFs');
    if (fs.existsSync(pcArchiveDir)) {
      await syncDirectoryAsync(pcArchiveDir, usbArchiveDir);
    }
    // Sync any remaining external roots (e.g. Downloads\JewelleryERP_Backups) without syncing usbArchiveDir twice
    await syncPcArchiveToExternalRootsAsync([usbArchiveDir]);

    lastSyncedDbMtime = getDbMtime(pcDbPath);
    lastSyncedArchiveSig = fs.existsSync(pcArchiveDir) ? await getDirChangeSignatureAsync(pcArchiveDir) : 'none';
    lastSyncTimestamp = new Date().toISOString();
    notifyStorageStatusChanged();

    if (parentWin && (!options || options.showDialog !== false)) {
      await dialog.showMessageBox(parentWin, {
        type: 'info',
        title: 'Store Backup Successful',
        message: `All store data & PDFs safely saved!\n\nDestination: ${targetName}\nLive DB: ${liveUsbDb}\nPDF Vault: ${usbArchiveDir}\nSnapshot Backup: ${snapshotDb}\n\nYour data is 100% crash-proof and portable.`
      });
    }

    return {
      success: true,
      usbName: targetName,
      livePath: liveUsbDb,
      archivePath: usbArchiveDir,
      snapshotPath: snapshotDb,
      timestamp
    };
  } catch (err) {
    if (parentWin && (!options || options.showDialog !== false)) {
      dialog.showErrorBox('Backup Error', `Failed to copy database: ${err.message}`);
    }
    return { success: false, error: err.message };
  } finally {
    isStorageSyncRunning = false;
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

function getPythonExecutable() {
  const candidates = [
    process.env.PYTHON_PATH,
    'C:\\Users\\YASH SONI\\AppData\\Local\\Programs\\Python\\Python313\\python.exe',
    path.join(process.env.LOCALAPPDATA || 'C:\\Users\\YASH SONI\\AppData\\Local', 'Programs', 'Python', 'Python313', 'python.exe'),
    path.join(process.env.LOCALAPPDATA || 'C:\\Users\\YASH SONI\\AppData\\Local', 'Programs', 'Python', 'Python312', 'python.exe'),
    path.join(process.env.LOCALAPPDATA || 'C:\\Users\\YASH SONI\\AppData\\Local', 'Programs', 'Python', 'Python311', 'python.exe'),
    'C:\\Python313\\python.exe',
    'C:\\Python312\\python.exe',
    'python.exe',
    'python'
  ];
  for (const c of candidates) {
    if (c && fs.existsSync(c)) return c;
  }
  return process.platform === 'win32' ? 'python' : 'python3';
}

function startBackend() {
  if (pythonProcess && !pythonProcess.killed) {
    try {
      process.kill(pythonProcess.pid, 0);
      console.log(`[Desktop] Backend already running on PID ${pythonProcess.pid}`);
      return;
    } catch (e) {
      pythonProcess = null;
    }
  }

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

    BACKEND_HOST: '127.0.0.1',

    ...(pdfBridgeUrl ? { ELECTRON_PDF_BRIDGE_URL: pdfBridgeUrl } : {}),

  };



  console.log(`[Desktop] Starting Backend with DATABASE_URL=${sqliteUrl}`);



  const scriptPath = path.join(backendDir, 'run_server.py');
  const pythonCmd = getPythonExecutable();

  // Priority 1: Standalone bundled executable (100% Zero-Dependency for any new laptop)
  if (fs.existsSync(standaloneBinary)) {
    console.log('[Desktop] Spawning Standalone Backend (Zero-Dependency): ' + standaloneBinary);
    pythonProcess = spawn(standaloneBinary, [], {
      cwd: path.dirname(standaloneBinary),
      env,
      stdio: ['ignore', 'pipe', 'pipe']
    });
  } else if (fs.existsSync(scriptPath) && pythonCmd) {
    console.log('[Desktop] Spawning Python interpreter with latest backend: ' + scriptPath + ' using ' + pythonCmd);
    pythonProcess = spawn(pythonCmd, [scriptPath], {
      cwd: backendDir,
      env,
      stdio: ['ignore', 'pipe', 'pipe']
    });
  } else {
    console.error('[Desktop] No valid backend found! Checked standalone: ' + standaloneBinary + ', script: ' + scriptPath);
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
            const defaultBackupDir = path.join(app.getPath('downloads'), 'JewelleryERP_Backups');
            const defaultDir = fs.existsSync(defaultBackupDir) ? defaultBackupDir : app.getPath('downloads');
            const { filePath } = await dialog.showSaveDialog(mainWindow, {
              title: 'Backup Jewellery ERP Database',
              defaultPath: path.join(defaultDir, `jewellery_erp_backup_${new Date().toISOString().slice(0, 10)}.db`),
              filters: [{ name: 'SQLite Database', extensions: ['db', 'sqlite'] }]
            });
            if (filePath && fs.existsSync(pcDbPath)) {
              await triggerCheckpoint();
              await safeCopySqliteDbAsync(pcDbPath, filePath);
              const destParent = path.dirname(filePath);
              const genericDirs = new Set([
                app.getPath('downloads').toLowerCase(),
                app.getPath('desktop').toLowerCase(),
                app.getPath('documents').toLowerCase(),
              ]);
              if (!genericDirs.has(path.resolve(destParent).toLowerCase())) {
                rememberCustomBackupDir(destParent);
                const pcArchiveDir = path.join(pcDir, 'Archived_PDFs');
                const backupArchiveDir = path.basename(destParent).toLowerCase() === 'jewelleryerp_backups'
                  ? path.join(destParent, 'JewelleryERP_Data', 'Archived_PDFs')
                  : path.join(destParent, 'Archived_PDFs');
                if (fs.existsSync(pcArchiveDir)) await syncDirectoryAsync(pcArchiveDir, backupArchiveDir);
              }
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

            const currentTitle = (mainWindow && !mainWindow.isDestroyed()) ? mainWindow.getTitle() : 'Jewellery ERP';
            dialog.showMessageBox(mainWindow, {

              type: 'info',

              title: currentTitle || 'Jewellery ERP Desktop',

              message: `${currentTitle || 'Jewellery ERP'} - Offline Edition v1.0\n\n100% Offline Standalone PC Application\nEmbedded SQLite Database with Continuous USB Pendrive Auto-Sync.`

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

    title: 'Jewellery ERP',

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



  // Allow dynamic title updates from renderer settings (page-title-updated not blocked)

  // Save browser downloads cleanly into the user's Downloads folder without cluttering Archived_PDFs
  mainWindow.webContents.session.on('will-download', (_event, item) => {
    try {
      const fileName = item.getFilename();
      const downloadsDir = app.getPath('downloads');
      if (!fs.existsSync(downloadsDir)) {
        fs.mkdirSync(downloadsDir, { recursive: true });
      }
      const finalSavePath = path.join(downloadsDir, fileName);
      item.setSavePath(finalSavePath);
      console.log(`[Download] Saved to ${finalSavePath}`);
    } catch (e) {
      console.error(`[Download Error] ${e ? e.message : ''}`);
    }
  });

  // Allow F1 through F12 function keys and Arrow keys to pass cleanly to web contents
  mainWindow.webContents.on('before-input-event', (event, input) => {
    // If user presses F1..F12, ensure Chromium does not hijack (e.g. F1 Windows Help)
    if (input.key === 'F1' || input.key === 'F3' || input.key === 'F5' || input.key === 'F11' || input.key === 'F12') {
      // Keydown allowed to fire in renderer
    }
  });



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
  isAppQuitting = true;
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





ipcMain.handle('open-pdf-vault-folder', async (_, target) => {

  const drives = getUsbDrives();

  let targetPath = path.join(pcDir, 'Archived_PDFs');

  if (target === 'usb' && drives.length > 0) {

    targetPath = path.join(drives[0].letter, 'JewelleryERP_Data', 'Archived_PDFs');

  }

  if (!fs.existsSync(targetPath)) {

    try { fs.mkdirSync(targetPath, { recursive: true }); } catch (e) {}

  }

  shell.openPath(targetPath);

  return { success: true, path: targetPath };

});



ipcMain.handle('delete-vault-pdf', async (_, { category, folderName, docNumber, docDate }) => {
  try {
    const roots = [path.join(pcDir, 'Archived_PDFs')];
    const drives = getUsbDrives();
    for (const drive of drives) {
      roots.push(path.join(drive.letter, 'JewelleryERP_Data', 'Archived_PDFs'));
    }
    const cleanDoc = (docNumber || '').toLowerCase().replace(/[^a-z0-9_-]/g, '_');
    const cleanDate = (docDate || '').toLowerCase().replace(/[^a-z0-9_-]/g, '-');
    for (const r of roots) {
      const catDir = path.join(r, category || 'Sales');
      if (!fs.existsSync(catDir)) continue;

      let searchDirs = [];
      if (folderName && fs.existsSync(path.join(catDir, folderName))) {
        searchDirs.push(path.join(catDir, folderName));
      } else {
        searchDirs = fs.readdirSync(catDir).map(d => path.join(catDir, d));
      }

      for (const d of searchDirs) {
        if (!fs.existsSync(d) || !fs.statSync(d).isDirectory()) continue;
        const files = fs.readdirSync(d);
        for (const f of files) {
          const fLower = f.toLowerCase();
          const matchesDoc = cleanDoc && fLower.includes(cleanDoc) && fLower.endsWith('.pdf');
          const matchesDate = cleanDate && (fLower === (cleanDate + '.pdf') || fLower.includes(cleanDate));
          if (matchesDoc || matchesDate) {
            try { fs.unlinkSync(path.join(d, f)); } catch (e) {}
          }
        }
        const remaining = fs.readdirSync(d).filter(f => !f.toLowerCase().startsWith('statement_'));
        if (remaining.length === 0) {
          for (const f of fs.readdirSync(d)) {
            try { fs.unlinkSync(path.join(d, f)); } catch (e) {}
          }
          try { fs.rmdirSync(d); } catch (e) {}
        }
      }
    }
    return { success: true };
  } catch (err) {
    return { success: false, error: err.message };
  }
});

ipcMain.handle('delete-party-folder', async (_, { category, folderName }) => {
  try {
    if (!folderName) return { success: false, error: 'No folderName provided' };
    const roots = [path.join(pcDir, 'Archived_PDFs')];
    const drives = getUsbDrives();
    if (drives.length > 0) {
      roots.push(path.join(drives[0].letter, 'JewelleryERP_Data', 'Archived_PDFs'));
    }
    const cleanTarget = folderName.toLowerCase();
    for (const r of roots) {
      const catDir = path.join(r, category || 'Sales');
      if (!fs.existsSync(catDir)) continue;

      const entries = fs.readdirSync(catDir);
      for (const e of entries) {
        const full = path.join(catDir, e);
        if (!fs.existsSync(full) || !fs.statSync(full).isDirectory()) continue;
        if (e.toLowerCase() === cleanTarget || e.toLowerCase().includes(cleanTarget)) {
          try {
            fs.rmSync(full, { recursive: true, force: true });
            console.log('[Desktop Delete Party] Removed folder ' + full);
          } catch (delErr) {
            console.error('[Desktop Delete Party Error] ' + (delErr ? delErr.message : ''));
          }
        }
      }
    }
    return { success: true };
  } catch (err) {
    return { success: false, error: err.message };
  }
});

ipcMain.handle('save-vault-pdf', async (_, { category, folderName, fileName, base64Data, isGst, companyId }) => {
  try {
    const rawFile = String(fileName || 'document.pdf').trim();
    const rawStem = rawFile.toLowerCase().endsWith('.pdf') ? rawFile.slice(0, -4) : rawFile;
    const cleanStem = sanitizeVaultName(rawStem, 'document');
    const cleanFileName = `${cleanStem}.pdf`;
    const cleanFolderName = sanitizeVaultName(folderName, 'Unknown');

    const rawCat = String(category || 'Sales').trim().toLowerCase();
    const cleanCategory = rawCat.startsWith('purch') ? 'Purchases' : (rawCat.startsWith('exch') ? 'Exchanges' : 'Sales');

    const fnUpper = cleanFileName.toUpperCase();
    const isGstDoc = Boolean(isGst || companyId === 2 || (
      fnUpper.startsWith('SJ_S') || fnUpper.startsWith('SJ_P') || fnUpper.startsWith('SJ_E') ||
      fnUpper.startsWith('PG_S') || fnUpper.startsWith('PG_P') || fnUpper.startsWith('PG_E') ||
      fnUpper.includes('_S_') || fnUpper.includes('_P_') || fnUpper.includes('_E_')
    ));
    const gstSubfolder = isGstDoc ? 'GST' : 'Without_GST';

    const pcArchiveDir = path.join(pcDir, 'Archived_PDFs', gstSubfolder, cleanCategory, cleanFolderName);
    await fs.promises.mkdir(pcArchiveDir, { recursive: true });

    const pcFilePath = path.join(pcArchiveDir, cleanFileName);
    const buffer = Buffer.from(base64Data, 'base64');
    await fs.promises.writeFile(pcFilePath, buffer);

    const cleanupObsolete = async (dirPath) => {
      try {
        const files = await fs.promises.readdir(dirPath);
        for (const f of files) {
          if (f !== cleanFileName && f.toLowerCase().endsWith('.pdf') && f.startsWith(`${cleanStem}_`)) {
            await fs.promises.unlink(path.join(dirPath, f)).catch(() => {});
          }
        }
      } catch {}
    };
    await cleanupObsolete(pcArchiveDir);

    // Mirror asynchronously across USB, Downloads backup, and remembered backup dirs without freezing UI
    await Promise.all(
      getAllExternalArchiveDirs().map(async (extArchiveRoot) => {
        try {
          const extDir = path.join(extArchiveRoot, gstSubfolder, cleanCategory, cleanFolderName);
          await fs.promises.mkdir(extDir, { recursive: true });
          await fs.promises.writeFile(path.join(extDir, cleanFileName), buffer);
          await cleanupObsolete(extDir);
        } catch (extErr) {
          console.warn(`[Vault Mirror Error on ${extArchiveRoot}]`, extErr.message);
        }
      })
    );

    return { success: true, path: pcFilePath };
  } catch (err) {
    console.error('[SaveVaultPdf Error]', err);
    return { success: false, error: err.message };
  }
});

ipcMain.handle('archive-pdfs-now', async (_, options = {}) => {
  const ok = await triggerPdfArchive(options);
  await syncPcArchiveToExternalRootsAsync();
  return { success: ok };
});

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
  const defaultBackupDir = path.join(app.getPath('downloads'), 'JewelleryERP_Backups');
  const defaultDir = fs.existsSync(defaultBackupDir) ? defaultBackupDir : app.getPath('downloads');
  const { filePath } = await dialog.showSaveDialog(mainWindow, {
    title: 'Backup Jewellery ERP Database',
    defaultPath: path.join(defaultDir, `jewellery_erp_backup_${new Date().toISOString().slice(0, 10)}.db`),
    filters: [{ name: 'SQLite Database', extensions: ['db', 'sqlite'] }]
  });
  if (filePath && fs.existsSync(pcDbPath)) {
    await triggerCheckpoint();
    await safeCopySqliteDbAsync(pcDbPath, filePath);
    const destParent = path.dirname(filePath);
    const genericDirs = new Set([
      app.getPath('downloads').toLowerCase(),
      app.getPath('desktop').toLowerCase(),
      app.getPath('documents').toLowerCase(),
    ]);
    if (!genericDirs.has(path.resolve(destParent).toLowerCase())) {
      rememberCustomBackupDir(destParent);
      const pcArchiveDir = path.join(pcDir, 'Archived_PDFs');
      const backupArchiveDir = path.basename(destParent).toLowerCase() === 'jewelleryerp_backups'
        ? path.join(destParent, 'JewelleryERP_Data', 'Archived_PDFs')
        : path.join(destParent, 'Archived_PDFs');
      if (fs.existsSync(pcArchiveDir)) await syncDirectoryAsync(pcArchiveDir, backupArchiveDir);
    }
    return { success: true, path: filePath };
  }
  return { success: false };
});

ipcMain.handle('backup-to-usb', async (_, options) => {
  if (!mainWindow) return { success: false };
  return await backupToUsb(mainWindow, options);
});



ipcMain.handle('restore-database', async () => {

  if (!mainWindow) return { success: false };

  return await restoreDatabase(mainWindow);

});



ipcMain.handle('open-external', (_, url) => {
  shell.openExternal(url);
});

async function withHiddenHtmlWindow(html, { width = 900, height = 1100, title = 'Document', restoreFocus = false } = {}, workFn) {
  if (!html || typeof html !== 'string') {
    return { success: false, error: 'Invalid HTML content' };
  }

  const tmpHtmlPath = path.join(
    app.getPath('temp'),
    `jewellery_erp_doc_${Date.now()}_${Math.random().toString(36).slice(2, 8)}.html`
  );

  let hiddenWin = null;
  const cleanup = () => {
    try {
      if (hiddenWin && !hiddenWin.isDestroyed()) {
        hiddenWin.destroy();
      }
    } catch {}
    try {
      if (fs.existsSync(tmpHtmlPath)) {
        fs.unlinkSync(tmpHtmlPath);
      }
    } catch {}
    if (restoreFocus && mainWindow && !mainWindow.isDestroyed()) {
      mainWindow.focus();
    }
  };

  try {
    // Strip remote Google Fonts stylesheet links so offline/slow network never stalls Chromium PDF/Print loading
    const localSafeHtml = html.replace(/<link[^>]*fonts\.googleapis\.com[^>]*>/gi, '');
    await fs.promises.writeFile(tmpHtmlPath, localSafeHtml, 'utf8');

    hiddenWin = new BrowserWindow({
      show: false,
      width,
      height,
      title,
      webPreferences: {
        contextIsolation: true,
        nodeIntegration: false,
        sandbox: false,
      },
    });

    const loaded = await new Promise((resolve) => {
      let done = false;
      let capTimer = null;
      const finishLoad = (ok, errMsg) => {
        if (done) return;
        done = true;
        if (capTimer) clearTimeout(capTimer);
        resolve({ ok, errMsg });
      };

      hiddenWin.webContents.once('did-fail-load', (_e, errorCode, errorDesc) => {
        finishLoad(false, `${errorDesc} (${errorCode})`);
      });

      hiddenWin.webContents.once('dom-ready', () => {
        // Never hang longer than 1.2s after DOM ready waiting for external resources
        capTimer = setTimeout(() => finishLoad(true), 1200);
      });

      hiddenWin.webContents.once('did-finish-load', async () => {
        try {
          await hiddenWin.webContents.executeJavaScript(`
            (async () => {
              if (document.fonts && document.fonts.ready) {
                await Promise.race([document.fonts.ready, new Promise(r => setTimeout(r, 150))]);
              }
              const imgs = Array.from(document.images || []);
              await Promise.race([
                Promise.all(imgs.map(img => img.complete ? Promise.resolve() : new Promise(res => {
                  img.addEventListener('load', res, { once: true });
                  img.addEventListener('error', res, { once: true });
                }))),
                new Promise(r => setTimeout(r, 350))
              ]);
            })();
          `);
        } catch {}
        finishLoad(true);
      });

      hiddenWin.loadFile(tmpHtmlPath).catch((err) => {
        finishLoad(false, err?.message || 'Failed to load HTML');
      });
    });

    if (!loaded.ok) {
      return { success: false, error: loaded.errMsg };
    }
    if (!hiddenWin || hiddenWin.isDestroyed()) {
      return { success: false, error: 'Render window closed prematurely' };
    }

    return await workFn(hiddenWin);
  } catch (err) {
    return { success: false, error: err?.message || 'Document processing failed' };
  } finally {
    cleanup();
  }
}

ipcMain.handle('print-html', async (_, { html, title } = {}) => {
  return await withHiddenHtmlWindow(
    html,
    { width: 900, height: 1100, title: title || 'Print Document', restoreFocus: true },
    (printWin) => new Promise((resolve) => {
      printWin.webContents.print(
        { silent: false, printBackground: true },
        (success, failureReason) => {
          resolve({
            success: Boolean(success),
            error: success ? undefined : (failureReason || 'cancelled'),
          });
        }
      );
    })
  );
});

async function renderHtmlToPdfBuffer(html, landscape = false) {
  return await withHiddenHtmlWindow(
    html,
    { width: landscape ? 1123 : 794, height: landscape ? 794 : 1123, title: 'PDF Export', restoreFocus: false },
    async (pdfWin) => {
      const pdfBuffer = await pdfWin.webContents.printToPDF({
        printBackground: true,
        pageSize: 'A4',
        landscape: Boolean(landscape),
        margins: { marginType: 'none' },
      });
      return {
        success: true,
        buffer: Buffer.from(pdfBuffer),
      };
    }
  );
}

function startPdfBridgeServer() {
  if (pdfBridgeServer && pdfBridgeUrl) {
    return Promise.resolve(pdfBridgeUrl);
  }
  return new Promise((resolve) => {
    const server = http.createServer((req, res) => {
      if (req.method !== 'POST' || req.url !== '/render-pdf') {
        res.writeHead(404);
        res.end();
        return;
      }
      const chunks = [];
      let totalBytes = 0;
      const MAX_BODY = 8 * 1024 * 1024;
      req.on('data', (chunk) => {
        totalBytes += chunk.length;
        if (totalBytes <= MAX_BODY) {
          chunks.push(chunk);
        }
      });
      req.on('end', async () => {
        if (totalBytes > MAX_BODY) {
          res.writeHead(413, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ success: false, error: 'Payload too large' }));
          return;
        }
        try {
          const payload = JSON.parse(Buffer.concat(chunks).toString('utf8'));
          const result = await renderHtmlToPdfBuffer(payload?.html, Boolean(payload?.landscape));
          if (result?.success && result.buffer) {
            res.writeHead(200, {
              'Content-Type': 'application/pdf',
              'Content-Length': result.buffer.length,
            });
            res.end(result.buffer);
          } else {
            res.writeHead(500, { 'Content-Type': 'application/json' });
            res.end(JSON.stringify({ success: false, error: result?.error || 'PDF render failed' }));
          }
        } catch (err) {
          res.writeHead(400, { 'Content-Type': 'application/json' });
          res.end(JSON.stringify({ success: false, error: err?.message || 'Invalid request' }));
        }
      });
    });

    server.on('error', (err) => {
      console.error('[Desktop] PDF Bridge error:', err.message);
      resolve('');
    });

    server.listen(0, '127.0.0.1', () => {
      const addr = server.address();
      pdfBridgeServer = server;
      pdfBridgeUrl = addr && typeof addr === 'object' ? `http://127.0.0.1:${addr.port}/render-pdf` : '';
      console.log(`[Desktop] Internal Chromium PDF Bridge listening at ${pdfBridgeUrl}`);
      resolve(pdfBridgeUrl);
    });
  });
}

ipcMain.handle('set-app-title', async (_, title) => {
  if (mainWindow && !mainWindow.isDestroyed() && title && String(title).trim()) {
    mainWindow.setTitle(String(title).trim());
    return { success: true };
  }
  return { success: false };
});

ipcMain.handle('html-to-pdf', async (_, { html, landscape = false } = {}) => {
  const result = await renderHtmlToPdfBuffer(html, landscape);
  if (result?.success && result.buffer) {
    return {
      success: true,
      base64: result.buffer.toString('base64'),
    };
  }
  return { success: false, error: result?.error || 'PDF export failed' };
});

ipcMain.handle('print-current-page', async () => {
  if (!mainWindow || mainWindow.isDestroyed()) {
    return { success: false, error: 'Main window unavailable' };
  }
  return await new Promise((resolve) => {
    mainWindow.webContents.print(
      { silent: false, printBackground: true },
      (success, failureReason) => {
        if (mainWindow && !mainWindow.isDestroyed()) {
          mainWindow.focus();
        }
        resolve({
          success: Boolean(success),
          error: success ? undefined : (failureReason || 'cancelled'),
        });
      }
    );
  });
});



// App Lifecycle

app.whenReady().then(async () => {

  // 1. Resolve startup storage: syncs PC <-> Pendrive if USB connected

  resolveDatabaseAtStartup();



  // 2. Start in-process Chromium PDF Bridge before backend so Python uses fast Electron rendering

  await startPdfBridgeServer();



  // 3. Start Backend

  startBackend();



  // 4. Start Storage Engine: non-blocking auto-mirror + USB insertion detection

  startStorageEngine();



  // 5. Open Single Desktop Window Immediately

  createWindow();

});



app.on('second-instance', () => {
  if (mainWindow) {
    if (mainWindow.isMinimized()) mainWindow.restore();
    if (!mainWindow.isVisible()) mainWindow.show();
    mainWindow.focus();

    try {
      const pingReq = http.get(`${BACKEND_URL}/ping`, (res) => {
        if (res.statusCode !== 200) {
          console.log('[Desktop] Backend unhealthy on second-instance. Reviving...');
          startBackend();
        }
      });
      pingReq.on('error', () => {
        console.log('[Desktop] Backend unreachable on second-instance. Reviving...');
        startBackend();
      });
      pingReq.setTimeout(1000, () => {
        pingReq.abort();
        console.log('[Desktop] Backend ping timed out on second-instance. Reviving...');
        startBackend();
      });
    } catch (e) {}
  } else {
    createWindow();
  }
});

app.on('before-quit', () => {
  isAppQuitting = true;
});



app.on('activate', () => {

  if (BrowserWindow.getAllWindows().length === 0) {

    createWindow();

  }

});



app.on('will-quit', () => {

  if (mirrorInterval) clearInterval(mirrorInterval);

  if (usbDetectionInterval) clearInterval(usbDetectionInterval);

  if (pdfBridgeServer) {
    try { pdfBridgeServer.close(); } catch (e) {}
    pdfBridgeServer = null;
  }

  flushStorageSync();

  killBackend();

});



app.on('window-all-closed', () => {

  if (mirrorInterval) clearInterval(mirrorInterval);

  if (usbDetectionInterval) clearInterval(usbDetectionInterval);

  if (pdfBridgeServer) {
    try { pdfBridgeServer.close(); } catch (e) {}
    pdfBridgeServer = null;
  }

  flushStorageSync();

  killBackend();

  if (process.platform !== 'darwin') {

    app.quit();

  }

});

