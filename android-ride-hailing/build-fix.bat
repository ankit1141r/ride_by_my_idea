@echo off
set JAVA_HOME=C:\Program Files\Java\jdk-21.0.10
echo JAVA_HOME set to: %JAVA_HOME%
gradlew.bat :core:ui:compileDebugKotlin --stacktrace
