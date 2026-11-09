path = r'C:\Users\YASH SONI\Desktop\jeweller-app\desktop\src\main.js'
with open(path, 'r', encoding='utf-8') as f:
    code = f.read()

target = """  if (fs.existsSync(standaloneBinary)) {

    console.log(`[Desktop] Spawning Standalone Backend: ${standaloneBinary}`);

    pythonProcess = spawn(standaloneBinary, [], {

      cwd: path.dirname(standaloneBinary),

      env,

      stdio: ['ignore', 'pipe', 'pipe']

    });

  } else {

    const pythonCmd = process.platform === 'win32' ? 'python' : 'python3';

    const scriptPath = path.join(backendDir, 'run_server.py');

    console.log(`[Desktop] Spawning Python interpreter: ${scriptPath}`);

    pythonProcess = spawn(pythonCmd, [scriptPath], {

      cwd: backendDir,

      env,

      stdio: ['ignore', 'pipe', 'pipe']

    });"""

replacement = """  const scriptPath = path.join(backendDir, 'run_server.py');
  if (fs.existsSync(scriptPath)) {
    const pythonCmd = process.platform === 'win32' ? 'python' : 'python3';
    console.log(`[Desktop] Spawning Python interpreter with latest backend: ${scriptPath}`);
    pythonProcess = spawn(pythonCmd, [scriptPath], {
      cwd: backendDir,
      env,
      stdio: ['ignore', 'pipe', 'pipe']
    });
  } else if (fs.existsSync(standaloneBinary)) {
    console.log(`[Desktop] Spawning Standalone Backend: ${standaloneBinary}`);
    pythonProcess = spawn(standaloneBinary, [], {
      cwd: path.dirname(standaloneBinary),
      env,
      stdio: ['ignore', 'pipe', 'pipe']
    });"""

if target in code:
    code = code.replace(target, replacement, 1)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(code)
    print("Successfully prioritized run_server.py in desktop/src/main.js")
else:
    print("Exact target not found, trying regex...")
    import re
    pattern = r'if\s*\(fs\.existsSync\(standaloneBinary\)\)\s*\{[\s\S]*?pythonProcess\s*=\s*spawn\(pythonCmd,\s*\[scriptPath\],\s*\{[\s\S]*?\}\);'
    code_new, count = re.subn(pattern, replacement, code, count=1)
    if count > 0:
        with open(path, 'w', encoding='utf-8') as f:
            f.write(code_new)
        print("Successfully prioritized run_server.py via regex!")
    else:
        print("Failed to match pattern!")
