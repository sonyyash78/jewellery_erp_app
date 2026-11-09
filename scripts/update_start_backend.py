import os

p = r"c:\Users\YASH SONI\Desktop\jeweller-app\desktop\src\main.js"
with open(p, "r", encoding="utf-8") as f:
    c = f.read()

is_crlf = "\r\n" in c
c_norm = c.replace("\r\n", "\n")

target = """function startBackend() {

  killOrphanedPortProcess(BACKEND_PORT);



  const sqliteUrl = `sqlite:///${pcDbPath.replace(/\\\\/g, '/')}`;



  const env = {

    ...process.env,

    PYTHONUNBUFFERED: '1',

    DATABASE_URL: sqliteUrl,

    OFFLINE_MODE: 'true',

    ENVIRONMENT: 'offline',

    SECRET_KEY: 'jewellery-erp-desktop-offline-secret-key-2026',

    INITIAL_ADMIN_PASSWORD: 'admin',

    BACKEND_PORT: String(BACKEND_PORT),

    BACKEND_HOST: '127.0.0.1'

  };



  console.log(`[Desktop] Starting Backend with DATABASE_URL=${sqliteUrl}`);



  const scriptPath = path.join(backendDir, 'run_server.py');

  if (fs.existsSync(scriptPath)) {

    const pythonCmd = process.platform === 'win32' ? 'python' : 'python3';

    console.log(`[Desktop] Spawning Python interpreter: ${scriptPath}`);

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

    });

  }

  pythonProcess.stdout.on('data', (d) => console.log(`[Backend] ${d.toString().trim()}`));

  pythonProcess.stderr.on('data', (d) => console.error(`[Backend] ${d.toString().trim()}`));

  pythonProcess.on('exit', (code, signal) => {

    console.log(`[Desktop] Backend process exited (code=${code}, signal=${signal})`);

  });

}"""

replacement = """function findPythonCmd() {
  const localCandidates = [
    path.join(process.env.LOCALAPPDATA || 'C:\\\\Users\\\\YASH SONI\\\\AppData\\\\Local', 'Programs', 'Python', 'Python313', 'python.exe'),
    path.join(process.env.LOCALAPPDATA || 'C:\\\\Users\\\\YASH SONI\\\\AppData\\\\Local', 'Programs', 'Python', 'Python312', 'python.exe'),
    path.join(process.env.LOCALAPPDATA || 'C:\\\\Users\\\\YASH SONI\\\\AppData\\\\Local', 'Programs', 'Python', 'Python311', 'python.exe'),
    'C:\\\\Users\\\\YASH SONI\\\\AppData\\\\Local\\\\Programs\\\\Python\\\\Python313\\\\python.exe',
    'C:\\\\Python313\\\\python.exe',
    'C:\\\\Python312\\\\python.exe',
    'C:\\\\Python311\\\\python.exe'
  ];
  for (const c of localCandidates) {
    if (fs.existsSync(c)) return c;
  }
  return process.platform === 'win32' ? 'python' : 'python3';
}

function startBackend() {
  killOrphanedPortProcess(BACKEND_PORT);

  const sqliteUrl = `sqlite:///${pcDbPath.replace(/\\\\/g, '/')}`;
  const pythonExecutable = findPythonCmd();
  const pythonDir = path.dirname(pythonExecutable);
  const extendedPath = `${pythonDir};${path.join(pythonDir, 'Scripts')};${process.env.PATH || ''}`;

  const env = {
    ...process.env,
    PATH: extendedPath,
    PYTHONUNBUFFERED: '1',
    DATABASE_URL: sqliteUrl,
    OFFLINE_MODE: 'true',
    ENVIRONMENT: 'offline',
    SECRET_KEY: 'jewellery-erp-desktop-offline-secret-key-2026',
    INITIAL_ADMIN_PASSWORD: 'admin',
    BACKEND_PORT: String(BACKEND_PORT),
    BACKEND_HOST: '127.0.0.1'
  };

  console.log(`[Desktop] Starting Backend with DATABASE_URL=${sqliteUrl}`);
  const scriptPath = path.join(backendDir, 'run_server.py');

  if (fs.existsSync(scriptPath)) {
    console.log(`[Desktop] Spawning Python interpreter (${pythonExecutable}): ${scriptPath}`);
    try {
      pythonProcess = spawn(pythonExecutable, [scriptPath], {
        cwd: backendDir,
        env,
        stdio: ['ignore', 'pipe', 'pipe']
      });
    } catch (err) {
      console.error('[Desktop] Failed to invoke spawn for python:', err);
    }
  } else if (fs.existsSync(standaloneBinary)) {
    console.log(`[Desktop] Spawning Standalone Backend: ${standaloneBinary}`);
    try {
      pythonProcess = spawn(standaloneBinary, [], {
        cwd: path.dirname(standaloneBinary),
        env,
        stdio: ['ignore', 'pipe', 'pipe']
      });
    } catch (err) {
      console.error('[Desktop] Failed to invoke spawn for standalone binary:', err);
    }
  }

  if (pythonProcess) {
    pythonProcess.on('error', (err) => {
      console.error('[Desktop] Backend process emitted error:', err);
      // Fallback to standalone binary if script failed
      if (fs.existsSync(standaloneBinary) && (!pythonProcess || pythonProcess.killed || pythonProcess.exitCode !== null)) {
        console.log(`[Desktop] Spawning fallback standalone binary: ${standaloneBinary}`);
        try {
          pythonProcess = spawn(standaloneBinary, [], {
            cwd: path.dirname(standaloneBinary),
            env,
            stdio: ['ignore', 'pipe', 'pipe']
          });
          if (pythonProcess.stdout) pythonProcess.stdout.on('data', (d) => console.log(`[Backend] ${d.toString().trim()}`));
          if (pythonProcess.stderr) pythonProcess.stderr.on('data', (d) => console.error(`[Backend] ${d.toString().trim()}`));
        } catch (e2) {
          console.error('[Desktop] Standalone fallback failed:', e2);
        }
      }
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
  }
}"""

if target not in c_norm:
    print("target not found")
    # let's search for startBackend
    idx = c_norm.find("function startBackend()")
    print("Found at:", idx)
    print("Snippet:")
    print(repr(c_norm[idx:idx+200]))
else:
    c_norm = c_norm.replace(target, replacement, 1)
    final_content = c_norm.replace("\n", "\r\n") if is_crlf else c_norm
    with open(p, "w", encoding="utf-8") as f:
        f.write(final_content)
    print("Updated startBackend successfully")
