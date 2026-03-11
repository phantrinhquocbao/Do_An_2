@echo off
title He Thong Du Bao HPG - Phan Trinh Quoc Bao
color 0B

echo 🚀 1. Dang khoi dong Backend (FastAPI)...
:: Mo cua so moi chay API
start cmd /k "cd /d D:\Do_An_2\backend && ..\.venv\Scripts\activate && python api.py"

echo ⏳ Dang doi 5 giay cho Backend on dinh...
timeout /t 5

echo 🎨 2. Dang khoi dong Giao dien Streamlit...
cd /d D:\Do_An_2\frontend
:: Quan trong: File cua fen ten la app.py nhe!
..\.venv\Scripts\activate && streamlit run app.py

pause