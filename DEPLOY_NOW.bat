@echo off
REM One-Click Deployment for Windows
REM This script deploys the RideConnect platform with Docker

echo ========================================
echo   RideConnect - One-Click Deployment
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed!
    echo Please install Python from https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [1/3] Checking Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not installed!
    echo Please install Docker Desktop from https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

echo [2/3] Running deployment script...
python deploy_public.py

echo.
echo [3/3] Deployment complete!
echo.
pause
