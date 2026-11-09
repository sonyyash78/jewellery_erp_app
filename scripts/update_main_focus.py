with open('desktop/src/main.js', 'r', encoding='utf-8') as f:
    text = f.read()

# 1. Add console message & error forwarding to webContents
old_ready = """  mainWindow.once('ready-to-show', () => {

    mainWindow.show();

    mainWindow.focus();

  });"""

new_ready = """  mainWindow.once('ready-to-show', () => {
    mainWindow.show();
    mainWindow.focus();
  });

  mainWindow.webContents.on('console-message', (event, level, message, line, sourceId) => {
    console.log(`[UI Console] [Level ${level}] ${message} (${sourceId}:${line})`);
  });

  mainWindow.webContents.on('did-fail-load', (event, errorCode, errorDescription, validatedURL) => {
    console.error(`[Desktop] UI Failed to load: ${errorDescription} (${errorCode}) at ${validatedURL}`);
  });

  mainWindow.webContents.on('render-process-gone', (event, details) => {
    console.error(`[Desktop] Renderer crashed/gone: ${details.reason} (exitCode: ${details.exitCode})`);
  });"""

assert old_ready in text, "old_ready not found in main.js"
text = text.replace(old_ready, new_ready, 1)

# 2. Update second-instance handler
old_sec = """app.on('second-instance', () => {

  if (mainWindow) {

    if (mainWindow.isMinimized()) mainWindow.restore();

    if (!mainWindow.isVisible()) mainWindow.show();

    mainWindow.focus();

  } else {

    createWindow();

  }

});"""

new_sec = """app.on('second-instance', () => {
  console.log('[Desktop] Second instance attempted. Focusing main window.');
  if (mainWindow) {
    if (mainWindow.isMinimized()) mainWindow.restore();
    if (!mainWindow.isVisible()) mainWindow.show();
    mainWindow.setAlwaysOnTop(true);
    mainWindow.focus();
    mainWindow.setAlwaysOnTop(false);
  } else {
    createWindow();
  }
});"""

assert old_sec in text, "old_sec not found in main.js"
text = text.replace(old_sec, new_sec, 1)

with open('desktop/src/main.js', 'w', encoding='utf-8') as f:
    f.write(text)
print("Updated desktop/src/main.js successfully!")
