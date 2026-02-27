@echo off
title HE THONG DU BAO VN30 - BAO
color 0A

cd /d D:\Do_An_2

echo ==========================================
echo    DANG KHOI DONG HE THONG (VUI LONG DOI)
echo ==========================================

echo.
echo 1. Dang mo Backend (FastAPI)...
start "BACKEND" cmd /k "cd backend && ..\.venv\Scripts\python.exe -m uvicorn api:app --reload"

:: Doi Backend khoi dong 3 giay
timeout /t 3

echo.
echo 2. Dang mo Frontend (Streamlit)...
start "FRONTEND" cmd /k "cd frontend && ..\.venv\Scripts\python.exe -m streamlit run app.py"

:: Doi Frontend khoi dong 4 giay roi ep mo Chrome
timeout /t 4
start http://localhost:8501

echo.
echo XONG! Dang ep mo trinh duyet...
pause