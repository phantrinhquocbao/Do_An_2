import os
import signal
import subprocess
import sys
import time
import webbrowser
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent
BACKEND_PORT = os.getenv("BACKEND_PORT", "8000")
FRONTEND_PORT = os.getenv("FRONTEND_PORT", "8501")
BACKEND_HOST = os.getenv("BACKEND_HOST", "127.0.0.1")
FRONTEND_HOST = os.getenv("FRONTEND_HOST", "127.0.0.1")


def start_process(command, cwd=None):
    return subprocess.Popen(command, cwd=cwd or ROOT_DIR)


def terminate_process(process):
    if process.poll() is not None:
        return

    process.terminate()
    try:
        process.wait(timeout=10)
    except subprocess.TimeoutExpired:
        process.kill()


def main():
    backend_cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "backend.api:app",
        "--host",
        BACKEND_HOST,
        "--port",
        BACKEND_PORT,
    ]
    frontend_cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        str(ROOT_DIR / "frontend" / "app.py"),
        "--server.address",
        FRONTEND_HOST,
        "--server.port",
        FRONTEND_PORT,
        "--browser.gatherUsageStats=false",
    ]

    backend = start_process(backend_cmd)
    time.sleep(3)
    frontend = start_process(frontend_cmd)

    if os.getenv("OPEN_BROWSER", "1") == "1":
        time.sleep(2)
        try:
            webbrowser.open(f"http://{FRONTEND_HOST}:{FRONTEND_PORT}")
        except Exception:
            pass

    def shutdown(*_args):
        terminate_process(frontend)
        terminate_process(backend)
        raise SystemExit(0)

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)

    try:
        while True:
            if backend.poll() is not None:
                terminate_process(frontend)
                raise SystemExit(backend.returncode or 1)
            if frontend.poll() is not None:
                terminate_process(backend)
                raise SystemExit(frontend.returncode or 0)
            time.sleep(1)
    finally:
        terminate_process(frontend)
        terminate_process(backend)


if __name__ == "__main__":
    main()
