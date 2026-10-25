const { app, BrowserWindow, ipcMain, dialog, shell, Menu } = require('electron');
const path = require('path');
const fs = require('fs');
const http = require('http');
const { spawn, exec } = require('child_process');

let mainWindow = null;
let pythonProcess = null;
const BACKEND_PORT = 8000;
const BACKEND_URL = `http://127.0.0.1:${BACKEND_PORT}`;

// Prepare Local SQLite Database in standard Windows AppData
const userDataPath = app.getPath('userData');
const dbDir = path.join(userDataPath, 'data');
if (!fs.existsSync(dbDir)) {
  fs.mkdirSync(dbDir, { recursive: true });
}
const dbPath = path.join(dbDir, 'jewellery_erp.db');

// Resolve Backend directory
const backendDir = app.isPackaged
  ? path.join(process.resourcesPath, 'backend')
  : path.resolve(__dirname, '../../backend');

// Resolve Frontend dist directory
const frontendDist = app.isPackaged
  ? path.join(process.resourcesPath, 'frontend/dist')
  : path.resolve(__dirname, '../../frontend/dist');

/**
 * Find working python executable on system
 */
function getPythonCommand() {
  if (process.platform === 'win32') {
    return 'python';
  }
  return 'python3';
}

/**
 * Start the Python FastAPI backend process
 */
function startBackend() {
  const pythonCmd = getPythonCommand();
  const env = {
    ...process.env,
    PYTHONUNBUFFERED: '1',
    DATABASE_URL: `sqlite:///${dbPath.replace(/\\/g, '/')}`,
    OFFLINE_MODE: 'true',
    ENVIRONMENT: 'offline',
    SECRET_KEY: 'jewellery-erp-desktop-offline-secret-key-2026',
    ALGORITHM: 'HS256',
    ACCESS_TOKEN_EXPIRE_MINUTES: '14400',
    INITIAL_ADMIN_PASSWORD: 'admin'
  };

  console.log(`[Desktop] Starting Backend at ${backendDir} with database at ${dbPath}`);

  pythonProcess = spawn(
    pythonCmd,
    ['-m', 'uvicorn', 'app.main:app', '--host', '127.0.0.1', '--port', String(BACKEND_PORT)],
    {
      cwd: backendDir,
      env,
      stdio: ['ignore', 'pipe', 'pipe']
    }
  );

  pythonProcess.stdout.on('data', (data) => {
    console.log(`[Backend] ${data.toString().trim()}`);
  });

  pythonProcess.stderr.on('data', (data) => {
    console.error(`[Backend] ${data.toString().trim()}`);
  });

  pythonProcess.on('exit', (code, signal) => {
    console.log(`[Desktop] Python backend exited with code ${code} and signal ${signal}`);
  });
}

/**
 * Poll http://127.0.0.1:8000/ping until ready
 */
function waitForBackend(callback, maxRetries = 60) {
  let attempts = 0;
  const check = () => {
    attempts++;
    const req = http.get(`${BACKEND_URL}/ping`, (res) => {
      if (res.statusCode === 200) {
        console.log('[Desktop] Backend is ready!');
        callback(null);
      } else {
        retry();
      }
    });

    req.on('error', () => {
      retry();
    });

    req.setTimeout(800, () => {
      req.abort();
      retry();
    });
  };

  const retry = () => {
    if (attempts >= maxRetries) {
      callback(new Error('Backend initialization timed out'));
    } else {
      setTimeout(check, 400);
    }
  };

  check();
}

/**
 * Create Application Menu with Database Backup & Quick Tools
 */
function createMenu() {
  const template = [
    {
      label: 'File',
      submenu: [
        {
          label: 'Backup Database (.db)...',
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
          label: 'Open Data Folder in Explorer',
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
        { role: 'reload', label: 'Reload Page' },
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
              message: 'Jewellery ERP - Offline Edition v1.0\nSaideep Jewellers\n\n100% Offline PC Desktop Application\nEmbedded SQLite Database.'
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
 * Create Main Desktop Window
 */
function createWindow() {
  mainWindow = new BrowserWindow({
    width: 1366,
    height: 850,
    minWidth: 1024,
    minHeight: 700,
    title: 'Jewellery ERP - Offline Desktop (Saideep Jewellers)',
    icon: path.join(__dirname, 'assets/icon.png'),
    backgroundColor: '#0f172a',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: false
    }
  });

  createMenu();

  // Load the frontend UI
  const indexPath = path.join(frontendDist, 'index.html');
  if (fs.existsSync(indexPath)) {
    mainWindow.loadFile(indexPath);
  } else {
    // Fallback during development if frontend not built yet
    mainWindow.loadURL('http://localhost:5174');
  }

  mainWindow.on('closed', () => {
    mainWindow = null;
  });
}

/**
 * Graceful backend termination
 */
function killBackend() {
  if (pythonProcess && pythonProcess.pid) {
    console.log(`[Desktop] Terminating Python process PID ${pythonProcess.pid}...`);
    try {
      if (process.platform === 'win32') {
        exec(`taskkill /pid ${pythonProcess.pid} /T /F`, (err) => {
          if (err) console.log('[Desktop] Taskkill completed or process was already closed.');
        });
      } else {
        pythonProcess.kill('SIGTERM');
      }
    } catch (e) {
      console.error('[Desktop] Error terminating backend:', e);
    }
    pythonProcess = null;
  }
}

// IPC Handlers
ipcMain.on('get-backend-url', (event) => {
  event.returnValue = BACKEND_URL;
});

ipcMain.handle('get-database-path', () => {
  return dbPath;
});

ipcMain.handle('open-database-folder', () => {
  shell.openPath(dbDir);
  return true;
});

ipcMain.handle('backup-database', async () => {
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

ipcMain.handle('open-external', (_, url) => {
  shell.openExternal(url);
});

// App Lifecycle
app.whenReady().then(() => {
  startBackend();
  waitForBackend((err) => {
    if (err) {
      dialog.showErrorBox(
        'Backend Initialization Error',
        'Could not start the local offline server. Please verify Python is installed on your PC.'
      );
    }
    createWindow();
  });

  app.on('activate', () => {
    if (BrowserWindow.getAllWindows().length === 0) {
      createWindow();
    }
  });
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
