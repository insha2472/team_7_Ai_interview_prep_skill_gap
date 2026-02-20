@echo off
setlocal
title PREPNOVA Demo Fixer

echo ======================================================
echo           PREPNOVA Demo Environment Fixer
echo ======================================================
echo.

echo [1/3] Closing any conflicting Python processes...
taskkill /F /IM python.exe /T 2>nul
echo Done.
echo.

echo [2/3] Preparing the Backend...
cd /d %~dp0
if not exist "venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment 'venv' not found.
    echo Please ensure you are running this from the backend folder.
    pause
    exit /b
)
echo.

echo [3/3] Starting Backend Server...
echo The server will start on http://127.0.0.1:8000
echo.
echo [TIPS]
echo - If it hangs at startup, check your .env database setting.
echo - I have enabled Local SQLite mode for maximum stability.
echo.

venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload

echo.
echo Server stopped.
pause
