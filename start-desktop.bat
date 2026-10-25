@echo off
title Jewellery ERP - Offline PC Desktop App
echo ========================================================
echo  Jewellery ERP - Offline Desktop Application
echo  Saideep Jewellers (100%% Offline - Embedded SQLite)
echo ========================================================
echo.

cd /d "%~dp0"

:: If packaged Windows .exe exists, launch it directly!
if exist "desktop\dist-electron\win-unpacked\Jewellery ERP Desktop.exe" (
    echo Launching native desktop application...
    start "" "desktop\dist-electron\win-unpacked\Jewellery ERP Desktop.exe"
    exit /b 0
)

echo [1/3] Verifying Python and Node environment...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH!
    echo Please install Python 3.10+ from python.org and add to PATH.
    pause
    exit /b 1
)

node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Node.js is not installed or not in PATH!
    echo Please install Node.js 18+ from nodejs.org.
    pause
    exit /b 1
)

echo [2/3] Checking Frontend build...
if not exist "frontend\dist\index.html" (
    echo Building frontend for offline desktop...
    call npm --prefix frontend run build
)

echo [3/3] Launching Jewellery ERP Desktop App...
cd desktop
npm start
