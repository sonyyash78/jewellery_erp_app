import os
import sys
import multiprocessing

# Windows PyInstaller support for multiprocessing/uvicorn
multiprocessing.freeze_support()

# Set base dir to ensure app imports resolve
base_dir = os.path.dirname(os.path.abspath(__file__))
if base_dir not in sys.path:
    sys.path.insert(0, base_dir)

os.environ.setdefault("OFFLINE_MODE", "true")
os.environ.setdefault("ENVIRONMENT", "offline")
os.environ.setdefault("SECRET_KEY", "jewellery-erp-desktop-offline-secret-key-2026")
os.environ.setdefault("INITIAL_ADMIN_PASSWORD", "admin")

from app.main import app
import uvicorn

if __name__ == "__main__":
    import time
    import socket

    port = int(os.environ.get("BACKEND_PORT", "8000"))
    host = os.environ.get("BACKEND_HOST", "127.0.0.1")
    print(f"[Jewellery ERP Backend] Starting offline server on {host}:{port}...")

    # Ensure port is released before calling uvicorn.run
    max_wait = 10
    start_t = time.time()
    while time.time() - start_t < max_wait:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                s.bind((host, port))
                # Successfully bound, port is free!
                break
            except OSError:
                print(f"[Jewellery ERP Backend] Port {port} is waiting to be freed. Retrying...")
                time.sleep(0.5)

    uvicorn.run(app, host=host, port=port, log_level="info")
