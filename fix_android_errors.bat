@echo off
cd android-ride-hailing
set JAVA_HOME=C:\Program Files\Java\jdk-21.0.10
echo Setting JAVA_HOME to: %JAVA_HOME%
echo.
echo Running Gradle build to identify errors...
echo.
gradlew.bat :core:ui:compileDebugKotlin --stacktrace > ..\android_build_errors.txt 2>&1
echo.
echo Build output saved to android_build_errors.txt
echo.
echo Showing compilation errors:
echo.
findstr /C:"error:" ..\android_build_errors.txt
cd ..
