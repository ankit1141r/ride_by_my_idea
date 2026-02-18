@echo off
REM Setup ngrok for public URL

echo ========================================
echo   RideConnect - Public URL Setup
echo ========================================
echo.

echo This will help you get a public URL for mobile access!
echo.

REM Check if ngrok is installed
ngrok version >nul 2>&1
if errorlevel 1 (
    echo ngrok is NOT installed
    echo.
    echo Please install ngrok:
    echo 1. Go to: https://ngrok.com/download
    echo 2. Download ngrok for Windows
    echo 3. Extract ngrok.exe
    echo 4. Move it to C:\Windows\System32\
    echo 5. Run this script again
    echo.
    pause
    exit /b 1
)

echo ngrok is installed!
echo.

echo Starting server...
start "RideConnect Server" python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

echo Waiting for server to start...
timeout /t 5 /nobreak >nul

echo.
echo Starting ngrok...
echo.
echo ========================================
echo   YOUR PUBLIC URL WILL APPEAR BELOW
echo ========================================
echo.
echo Copy the "Forwarding" URL (https://xxxxx.ngrok.io)
echo Add /web/ at the end
echo Example: https://abc123.ngrok.io/web/
echo.
echo Share this URL to access from mobile!
echo.
echo Login: +919876543210 / password123
echo.
echo Press Ctrl+C to stop
echo ========================================
echo.

ngrok http 8000

pause
