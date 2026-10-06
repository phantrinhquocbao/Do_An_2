@echo off
setlocal
title DO_AN_2 - Phan Trinh Quoc Bao
color 0B

cd /d "%~dp0"

if not exist ".venv\Scripts\python.exe" (
    echo [1/3] Dang tao moi truong ao...
    python -m venv .venv
    if errorlevel 1 (
        echo Khong tao duoc .venv. Hay kiem tra Python da cai va co trong PATH.
        pause
        exit /b 1
    )
)

echo [2/3] Dang cai thu vien can thiet...
".venv\Scripts\python.exe" -m pip install --upgrade pip
if errorlevel 1 (
    echo Khong the nang cap pip.
    pause
    exit /b 1
)

".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
    echo Khong the cai dat thu vien tu requirements.txt.
    pause
    exit /b 1
)

echo [3/3] Dang khoi dong he thong...
".venv\Scripts\python.exe" run_do_an.py

endlocal
