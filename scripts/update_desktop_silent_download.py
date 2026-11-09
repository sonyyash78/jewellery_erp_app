def update_main_js():
    path = r"C:\Users\YASH SONI\Desktop\jeweller-app\desktop\src\main.js"
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()

    target = "  mainWindow.on('page-title-updated', (e) => e.preventDefault());"
    addition = """  mainWindow.on('page-title-updated', (e) => e.preventDefault());

  // Intercept all downloads to silently save PDFs directly into Archived_PDFs without showing the "Save As" location popup
  mainWindow.webContents.session.on('will-download', (event, item, webContents) => {
    try {
      const fileName = item.getFilename();
      const saveDir = path.join(pcDir, 'Archived_PDFs', 'Sales');
      if (!fs.existsSync(saveDir)) {
        fs.mkdirSync(saveDir, { recursive: true });
      }
      const finalSavePath = path.join(saveDir, fileName);
      item.setSavePath(finalSavePath);
      log.info(`[Silent-Save] Download saved to ${finalSavePath}`);
    } catch (e) {
      log.error(`[Silent-Save Error] ${e.message}`);
    }
  });"""

    if target in content and "mainWindow.webContents.session.on('will-download'" not in content:
        content = content.replace(target, addition)
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print("Added silent will-download handler to desktop/src/main.js")
    else:
        print("Target not found or will-download already added")

if __name__ == "__main__":
    update_main_js()
