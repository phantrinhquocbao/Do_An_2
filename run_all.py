import subprocess
import time
import os

def run_project():
    # 1. Chạy Backend (FastAPI) trong một tiến trình riêng
    print("🚀 Đang khởi động Backend...")
    backend_path = os.path.join(os.getcwd(), "backend", "api.py")
    subprocess.Popen(["python", backend_path])

    # 2. Đợi 5 giây cho API kịp bắt máy
    time.sleep(5)

    # 3. Chạy Frontend (Streamlit)
    print("🎨 Đang khởi động Giao diện...")
    frontend_path = os.path.join(os.getcwd(), "frontend", "chay_do_an.py")
    subprocess.run(["streamlit", "run", frontend_path])

if __name__ == "__main__":
    run_project()