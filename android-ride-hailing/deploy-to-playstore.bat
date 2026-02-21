@echo off
REM RideConnect - Google Play Store Deployment Script (Windows)
REM This script automates the build process for Play Store submission

echo =========================================
echo RideConnect Play Store Deployment
echo =========================================
echo.

REM Check if keystore.properties exists
if not exist "keystore.properties" (
    echo [ERROR] keystore.properties not found!
    echo Please create keystore.properties with your signing credentials.
    echo See GOOGLE_PLAY_DEPLOYMENT_GUIDE.md for details.
    exit /b 1
)

echo [OK] Found keystore.properties

REM Check if keystores exist
if not exist "rider-app\release-keystore.jks" (
    echo [WARNING] rider-app\release-keystore.jks not found
    echo Please generate the keystore first. See Step 2 in deployment guide.
    exit /b 1
)

if not exist "driver-app\release-keystore.jks" (
    echo [WARNING] driver-app\release-keystore.jks not found
    echo Please generate the keystore first. See Step 2 in deployment guide.
    exit /b 1
)

echo [OK] Found signing keystores
echo.

REM Clean previous builds
echo Cleaning previous builds...
call gradlew.bat clean
echo [OK] Clean complete
echo.

REM Build Rider App
echo =========================================
echo Building Rider App Release AAB...
echo =========================================
call gradlew.bat :rider-app:bundleRelease

if exist "rider-app\build\outputs\bundle\release\rider-app-release.aab" (
    echo [OK] Rider App AAB built successfully
    echo   Location: rider-app\build\outputs\bundle\release\rider-app-release.aab
    
    REM Verify signing
    echo   Verifying signature...
    jarsigner -verify -verbose -certs rider-app\build\outputs\bundle\release\rider-app-release.aab >nul 2>&1
    if %errorlevel% equ 0 (
        echo   [OK] Signature verified
    ) else (
        echo   [ERROR] Signature verification failed
        exit /b 1
    )
) else (
    echo [ERROR] Rider App build failed
    exit /b 1
)
echo.

REM Build Driver App
echo =========================================
echo Building Driver App Release AAB...
echo =========================================
call gradlew.bat :driver-app:bundleRelease

if exist "driver-app\build\outputs\bundle\release\driver-app-release.aab" (
    echo [OK] Driver App AAB built successfully
    echo   Location: driver-app\build\outputs\bundle\release\driver-app-release.aab
    
    REM Verify signing
    echo   Verifying signature...
    jarsigner -verify -verbose -certs driver-app\build\outputs\bundle\release\driver-app-release.aab >nul 2>&1
    if %errorlevel% equ 0 (
        echo   [OK] Signature verified
    ) else (
        echo   [ERROR] Signature verification failed
        exit /b 1
    )
) else (
    echo [ERROR] Driver App build failed
    exit /b 1
)
echo.

REM Summary
echo =========================================
echo Build Summary
echo =========================================
echo [OK] Both apps built successfully!
echo.
echo Release files:
echo   1. rider-app\build\outputs\bundle\release\rider-app-release.aab
echo   2. driver-app\build\outputs\bundle\release\driver-app-release.aab
echo.
echo Next steps:
echo   1. Go to Google Play Console: https://play.google.com/console
echo   2. Create new releases for both apps
echo   3. Upload the AAB files
echo   4. Add release notes
echo   5. Submit for review
echo.
echo See GOOGLE_PLAY_DEPLOYMENT_GUIDE.md for detailed instructions.
echo.
echo [SUCCESS] Deployment build complete!

pause
