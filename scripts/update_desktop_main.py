import os

p = r"c:\Users\YASH SONI\Desktop\jeweller-app\desktop\src\main.js"
with open(p, "r", encoding="utf-8") as f:
    c = f.read()

# Normalize line endings for replacement
is_crlf = "\r\n" in c
c_norm = c.replace("\r\n", "\n")

target1 = """const frontendDist = app.isPackaged

  ? path.join(process.resourcesPath, 'frontend/dist')

  : path.resolve(__dirname, '../../frontend/dist');"""

replacement1 = """function resolveFrontendDist() {
  if (app.isPackaged) {
    const candidates = [
      path.join(process.resourcesPath, 'frontend'),
      path.join(process.resourcesPath, 'frontend', 'dist'),
      path.join(__dirname, 'frontend'),
      path.join(__dirname, 'frontend', 'dist')
    ];
    for (const c of candidates) {
      if (fs.existsSync(path.join(c, 'index.html'))) {
        return c;
      }
    }
    return path.join(process.resourcesPath, 'frontend');
  }
  const devCandidates = [
    path.resolve(__dirname, '../../frontend/dist'),
    path.resolve(__dirname, '../frontend/dist'),
    path.resolve(__dirname, '../../frontend')
  ];
  for (const c of devCandidates) {
    if (fs.existsSync(path.join(c, 'index.html'))) {
      return c;
    }
  }
  return path.resolve(__dirname, '../../frontend/dist');
}

const frontendDist = resolveFrontendDist();"""

target2 = """  const indexPath = path.join(frontendDist, 'index.html');

  if (fs.existsSync(indexPath)) {

    mainWindow.loadFile(indexPath);

  } else {

    mainWindow.loadURL('http://localhost:5174');

  }"""

replacement2 = """  const candidateIndexPaths = [
    path.join(frontendDist, 'index.html'),
    path.join(process.resourcesPath, 'frontend', 'index.html'),
    path.join(process.resourcesPath, 'frontend', 'dist', 'index.html'),
    path.resolve(__dirname, '../../frontend/dist/index.html'),
    path.resolve(__dirname, '../frontend/dist/index.html')
  ];
  let indexPath = null;
  for (const p of candidateIndexPaths) {
    if (fs.existsSync(p)) {
      indexPath = p;
      break;
    }
  }

  if (indexPath) {
    console.log(`[Desktop] Loading UI from: ${indexPath}`);
    mainWindow.loadFile(indexPath).catch((err) => {
      console.error('[Desktop] Failed to load index.html:', err);
    });
  } else if (!app.isPackaged) {
    console.log('[Desktop] Development mode: loading http://localhost:5174');
    mainWindow.loadURL('http://localhost:5174').catch((err) => {
      console.error('[Desktop] Failed to load localhost:5174:', err);
    });
  } else {
    console.error('[Desktop] Critical: index.html not found among candidates:', candidateIndexPaths);
    mainWindow.loadURL(`data:text/html,<html><body style="background:#0f172a;color:#f87171;font-family:sans-serif;padding:30px;"><h2>Jewellery ERP Offline</h2><p>Frontend assets not found. Checked locations:</p><pre>${candidateIndexPaths.join('<br>')}</pre></body></html>`);
  }"""

if target1 not in c_norm:
    print("target1 not found in normalized content")
else:
    c_norm = c_norm.replace(target1, replacement1, 1)
    print("Replaced target1")

if target2 not in c_norm:
    print("target2 not found in normalized content")
else:
    c_norm = c_norm.replace(target2, replacement2, 1)
    print("Replaced target2")

final_content = c_norm.replace("\n", "\r\n") if is_crlf else c_norm
with open(p, "w", encoding="utf-8") as f:
    f.write(final_content)

print("Saved main.js")
