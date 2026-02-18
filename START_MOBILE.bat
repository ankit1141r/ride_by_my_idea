@echo off
REM Start server for mobile access

echo ========================================
echo   RideConnect - Mobile Access
echo ========================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed!
    pause
    exit /b 1
)

echo Starting mobile-accessible server...
echo.

python start_mobile.py

pause
