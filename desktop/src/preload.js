const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  isElectron: true,
  platform: process.platform,
  getBackendUrl: () => ipcRenderer.sendSync('get-backend-url'),
  getDatabasePath: () => ipcRenderer.invoke('get-database-path'),
  getStorageStatus: () => ipcRenderer.invoke('get-storage-status'),
  openDatabaseFolder: () => ipcRenderer.invoke('open-database-folder'),
  backupDatabase: () => ipcRenderer.invoke('backup-database'),
  backupToUsb: () => ipcRenderer.invoke('backup-to-usb'),
  syncNow: () => ipcRenderer.invoke('sync-now'),
  restoreDatabase: () => ipcRenderer.invoke('restore-database'),
  openExternal: (url) => ipcRenderer.invoke('open-external', url),
  onStorageStatusChange: (callback) => {
    const handler = (_event, data) => callback(data);
    ipcRenderer.on('storage-status-changed', handler);
    return () => ipcRenderer.removeListener('storage-status-changed', handler);
  }
});
