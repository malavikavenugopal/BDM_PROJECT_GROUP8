@echo off
title Aethelgard Leatherworks - BDM Dashboard
echo =====================================================================
echo  AETHELGARD LEATHERWORKS - BDM PLATFORM LAUNCHER
echo =====================================================================
echo.

echo [1/3] Checking dependencies...
pip install -r requirements.txt --quiet

echo [2/3] Starting Flask Application Server...
start "" http://localhost:5000

echo [3/3] Launching Web Server on http://localhost:5000 ...
python server.py
pause
