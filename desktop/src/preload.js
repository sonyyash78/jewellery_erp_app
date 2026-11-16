const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('electronAPI', {
  isElectron: true,
  platform: process.platform,
  getBackendUrl: () => ipcRenderer.sendSync('get-backend-url'),
  getDatabasePath: () => ipcRenderer.invoke('get-database-path'),
  getStorageStatus: () => ipcRenderer.invoke('get-storage-status'),
  openDatabaseFolder: () => ipcRenderer.invoke('open-database-folder'),
  openPdfVaultFolder: (target) => ipcRenderer.invoke('open-pdf-vault-folder', target),
  saveVaultPdf: (params) => ipcRenderer.invoke('save-vault-pdf', params),
  deleteVaultPdf: (params) => ipcRenderer.invoke('delete-vault-pdf', params),
  deletePartyFolder: (params) => ipcRenderer.invoke('delete-party-folder', params),
  archivePdfsNow: (options) => ipcRenderer.invoke('archive-pdfs-now', options),
  backupDatabase: () => ipcRenderer.invoke('backup-database'),
  backupToUsb: (options) => ipcRenderer.invoke('backup-to-usb', options),
  syncNow: () => ipcRenderer.invoke('sync-now'),
  restoreDatabase: () => ipcRenderer.invoke('restore-database'),
  openExternal: (url) => ipcRenderer.invoke('open-external', url),
  printHtml: (params) => ipcRenderer.invoke('print-html', params),
  htmlToPdf: (params) => ipcRenderer.invoke('html-to-pdf', params),
  printCurrentPage: () => ipcRenderer.invoke('print-current-page'),
  setAppTitle: (title) => ipcRenderer.invoke('set-app-title', title),
  onStorageStatusChange: (callback) => {
    const handler = (_event, data) => callback(data);
    ipcRenderer.on('storage-status-changed', handler);
    return () => ipcRenderer.removeListener('storage-status-changed', handler);
  }
});
