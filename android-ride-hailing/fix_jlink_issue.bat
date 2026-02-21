@echo off
echo Fixing jlink/JDK image issue...
echo.

echo Step 1: Stopping Gradle daemon...
call gradlew.bat --stop

echo.
echo Step 2: Clearing transforms cache...
rmdir /s /q "%USERPROFILE%\.gradle\caches\transforms-3" 2>nul

echo.
echo Step 3: Clearing jars cache...
rmdir /s /q "%USERPROFILE%\.gradle\caches\jars-*" 2>nul

echo.
echo Step 4: Clearing build cache...
rmdir /s /q "%USERPROFILE%\.gradle\caches\build-cache-*" 2>nul

echo.
echo Step 5: Cleaning project build directories...
call gradlew.bat clean

echo.
echo Fix applied! Now try building again with:
echo gradlew.bat assembleDebug
echo.
pause
