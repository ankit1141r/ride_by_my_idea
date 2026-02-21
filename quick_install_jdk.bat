@echo off
echo ============================================================
echo Quick JDK 17 Installation
echo ============================================================
echo.

echo Checking if winget is available...
winget --version >nul 2>&1
if %errorlevel% neq 0 (
    echo winget not found. Trying chocolatey...
    choco --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo.
        echo Neither winget nor chocolatey found.
        echo Please install JDK manually from: https://adoptium.net/
        pause
        exit /b 1
    )
    echo Installing JDK 17 with chocolatey...
    choco install temurin17 -y
) else (
    echo Installing JDK 17 with winget...
    winget install EclipseAdoptium.Temurin.17.JDK --silent --accept-package-agreements --accept-source-agreements
)

echo.
echo ============================================================
echo Installation complete!
echo ============================================================
echo.
echo Please close this window and open a NEW terminal, then run:
echo   java -version
echo.
echo If java is not recognized, you may need to restart your computer.
echo.
pause
