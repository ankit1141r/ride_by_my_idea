@echo off
echo Stopping any process on port 8000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000 "') do (
    taskkill /F /PID %%a >nul 2>&1
)
timeout /t 1 /nobreak >nul

echo Starting Ride-Hailing Platform...
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000
