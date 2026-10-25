const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  isElectron: true,
  platform: process.platform,
  getBackendUrl: () => ipcRenderer.sendSync('get-backend-url'),
  getDatabasePath: () => ipcRenderer.invoke('get-database-path'),
  openDatabaseFolder: () => ipcRenderer.invoke('open-database-folder'),
  backupDatabase: () => ipcRenderer.invoke('backup-database'),
  openExternal: (url) => ipcRenderer.invoke('open-external', url),
});
