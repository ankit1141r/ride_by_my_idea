@echo off
set "JAVA_HOME=C:\Program Files\Eclipse Adoptium\jdk-17.0.18.8-hotspot"
set "PATH=%JAVA_HOME%\bin;%PATH%"

echo ============================================================
echo Java Environment Configured!
echo ============================================================
echo JAVA_HOME=%JAVA_HOME%
echo.
echo Verifying installation...
java -version
echo.
echo ============================================================
echo Environment is ready for current session!
echo ============================================================
echo.
echo To build Android apps, run:
echo   cd android-ride-hailing
echo   gradlew.bat assembleDebug
echo.
