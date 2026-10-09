"""Unified Development Server Runner for Stick Clash.
Runs backend, frontend, and Cloudflare Tunnel concurrently.
"""

import os
import subprocess
import sys
import time

PYTHON_VENV = r"F:\project D\backend\venv\Scripts\python.exe"
FRONTEND_DIR = r"F:\project D\frontend"
TOOLS_DIR = r"F:\project D\tools"

def main():
    print("=" * 60)
    print("🚀 LAUNCHING STICK CLASH MICROSERVICES DEVELOPMENT SERVERS")
    print("=" * 60)

    # 1. Start Backend FastAPI
    print("[1/3] Starting Backend (FastAPI on http://127.0.0.1:8000)...")
    backend_proc = subprocess.Popen(
        [PYTHON_VENV, "-m", "uvicorn", "app.main:app", "--port", "8000"],
        cwd=r"F:\project D\backend",
    )

    # 2. Start Frontend Vite
    print("[2/3] Starting Frontend (Vite on http://127.0.0.1:5173)...")
    frontend_proc = subprocess.Popen(
        ["cmd.exe", "/c", "npm", "run", "dev"],
        cwd=FRONTEND_DIR,
    )

    time.sleep(2)

    # 3. Start Cloudflare Tunnel
    print("[3/3] Launching Cloudflare Tunnel for Public Online URL...")
    tunnel_proc = subprocess.Popen(
        [PYTHON_VENV, os.path.join(TOOLS_DIR, "run_tunnel.py"), "http://127.0.0.1:5173"],
        cwd=r"F:\project D",
    )

    print("\n[✓] All services active. Press Ctrl+C to stop all servers.\n")
    try:
        backend_proc.wait()
        frontend_proc.wait()
        tunnel_proc.wait()
    except KeyboardInterrupt:
        print("\n[*] Shutting down servers...")
        backend_proc.terminate()
        frontend_proc.terminate()
        tunnel_proc.terminate()

if __name__ == "__main__":
    main()
