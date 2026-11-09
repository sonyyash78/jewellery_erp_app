from pathlib import Path

main_path = Path(r'C:\Users\YASH SONI\Desktop\jeweller-app\desktop\src\main.js')
content = main_path.read_text(encoding='utf-8')

# 1. Add file logging hook right after pcDbPath
hook_code = """const pcDbPath = path.join(pcDir, 'jewellery_erp.db');

const desktopLogFile = path.join(pcDir, 'desktop_debug.log');
const origLog = console.log;
const origErr = console.error;
console.log = (...args) => {
  try { fs.appendFileSync(desktopLogFile, `[LOG ${new Date().toISOString()}] ${args.join(' ')}\\n`); } catch (e) {}
  origLog.apply(console, args);
};
console.error = (...args) => {
  try { fs.appendFileSync(desktopLogFile, `[ERR ${new Date().toISOString()}] ${args.join(' ')}\\n`); } catch (e) {}
  origErr.apply(console, args);
};
"""

content = content.replace("const pcDbPath = path.join(pcDir, 'jewellery_erp.db');", hook_code, 1)

# 2. Update getPythonExecutable candidates
old_py_func = """function getPythonExecutable() {
  const candidates = [
    process.env.PYTHON_PATH,
    path.join(process.env.LOCALAPPDATA || '', 'Programs', 'Python', 'Python313', 'python.exe'),
    path.join(process.env.LOCALAPPDATA || '', 'Programs', 'Python', 'Python312', 'python.exe'),
    path.join(process.env.LOCALAPPDATA || '', 'Programs', 'Python', 'Python311', 'python.exe'),
    'C:\\\\Python313\\\\python.exe',
    'C:\\\\Python312\\\\python.exe',
    'python.exe',
    'python'
  ];"""

new_py_func = """function getPythonExecutable() {
  const candidates = [
    process.env.PYTHON_PATH,
    'C:\\\\Users\\\\YASH SONI\\\\AppData\\\\Local\\\\Programs\\\\Python\\\\Python313\\\\python.exe',
    path.join(process.env.LOCALAPPDATA || 'C:\\\\Users\\\\YASH SONI\\\\AppData\\\\Local', 'Programs', 'Python', 'Python313', 'python.exe'),
    path.join(process.env.LOCALAPPDATA || 'C:\\\\Users\\\\YASH SONI\\\\AppData\\\\Local', 'Programs', 'Python', 'Python312', 'python.exe'),
    path.join(process.env.LOCALAPPDATA || 'C:\\\\Users\\\\YASH SONI\\\\AppData\\\\Local', 'Programs', 'Python', 'Python311', 'python.exe'),
    'C:\\\\Python313\\\\python.exe',
    'C:\\\\Python312\\\\python.exe',
    'python.exe',
    'python'
  ];"""

content = content.replace(old_py_func, new_py_func, 1)

# 3. Update pythonProcess event handlers in startBackend
old_events = """  pythonProcess.stdout.on('data', (d) => console.log(`[Backend] ${d.toString().trim()}`));
  pythonProcess.stderr.on('data', (d) => console.error(`[Backend] ${d.toString().trim()}`));
  pythonProcess.on('exit', (code, signal) => {
    console.log(`[Desktop] Backend process exited (code=${code}, signal=${signal})`);
  });"""

new_events = """  if (pythonProcess) {
    pythonProcess.on('error', (err) => {
      console.error(`[Desktop] Backend spawn error: ${err.message}`);
    });
    if (pythonProcess.stdout) {
      pythonProcess.stdout.on('data', (d) => console.log(`[Backend] ${d.toString().trim()}`));
    }
    if (pythonProcess.stderr) {
      pythonProcess.stderr.on('data', (d) => console.error(`[Backend] ${d.toString().trim()}`));
    }
    pythonProcess.on('exit', (code, signal) => {
      console.log(`[Desktop] Backend process exited (code=${code}, signal=${signal})`);
    });
  } else {
    console.error('[Desktop] Failed to spawn backend process');
  }"""

content = content.replace(old_events, new_events, 1)

main_path.write_text(content, encoding='utf-8')
print("main.js patched with logging, safe spawn, and exact python path!")
