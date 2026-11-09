p = r'C:\Users\YASH SONI\Desktop\jeweller-app\desktop\src\main.js'
with open(p, 'r', encoding='utf-8') as f:
    text = f.read()

python_helper = '''function getPythonExecutable() {
  const candidates = [
    process.env.PYTHON_PATH,
    path.join(process.env.LOCALAPPDATA || '', 'Programs', 'Python', 'Python313', 'python.exe'),
    path.join(process.env.LOCALAPPDATA || '', 'Programs', 'Python', 'Python312', 'python.exe'),
    path.join(process.env.LOCALAPPDATA || '', 'Programs', 'Python', 'Python311', 'python.exe'),
    'C:\\\\Python313\\\\python.exe',
    'C:\\\\Python312\\\\python.exe',
    'python.exe',
    'python'
  ];
  for (const c of candidates) {
    if (c && fs.existsSync(c)) return c;
  }
  return process.platform === 'win32' ? 'python' : 'python3';
}
'''

if 'function getPythonExecutable()' not in text:
    # Insert helper before function startBackend
    target = 'function startBackend()'
    text = text.replace(target, python_helper + '\n' + target, 1)
    print("Added getPythonExecutable helper!")

old_cmd = "const pythonCmd = process.platform === 'win32' ? 'python' : 'python3';"
new_cmd = "const pythonCmd = getPythonExecutable();"

if old_cmd in text:
    text = text.replace(old_cmd, new_cmd, 1)
    print("Replaced pythonCmd with getPythonExecutable()!")

with open(p, 'w', encoding='utf-8') as f:
    f.write(text)
print("Saved main.js")
