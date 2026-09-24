@echo off
title SAIDEEP JEWELLERS - Mobile App Dedicated Backend (Port 8001 / Database: jeweller_app_db)
echo ========================================================
echo Starting Mobile App Dedicated Backend Server (Port 8001)
echo Connected Database: jeweller_app_db (100%% Independent)
echo ========================================================
cd /d "C:\Users\YASH SONI\Desktop\jeweller-app\backend"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
pause
