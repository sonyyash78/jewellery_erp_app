@echo off
echo === Jeweller App Backend (Independent) ===
echo.
cd /d "%~dp0backend"

if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)

echo Activating venv...
call venv\Scripts\activate

echo Installing dependencies...
pip install -r requirements.txt -q

echo.
echo Starting FastAPI server on 0.0.0.0:8000...
echo Access from mobile: http://YOUR_PC_IP:8000
echo.
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
