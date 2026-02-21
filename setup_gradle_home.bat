@echo off
echo Creating Gradle home configuration...

set GRADLE_USER_HOME=%USERPROFILE%\.gradle

if not exist "%GRADLE_USER_HOME%" mkdir "%GRADLE_USER_HOME%"

echo org.gradle.jvmargs=-Xmx4096m -Dfile.encoding=UTF-8 --add-opens=jdk.compiler/com.sun.tools.javac.main=ALL-UNNAMED --add-opens=jdk.compiler/com.sun.tools.javac.code=ALL-UNNAMED --add-opens=jdk.compiler/com.sun.tools.javac.comp=ALL-UNNAMED --add-opens=jdk.compiler/com.sun.tools.javac.file=ALL-UNNAMED --add-opens=jdk.compiler/com.sun.tools.javac.jvm=ALL-UNNAMED --add-opens=jdk.compiler/com.sun.tools.javac.parser=ALL-UNNAMED --add-opens=jdk.compiler/com.sun.tools.javac.processing=ALL-UNNAMED --add-opens=jdk.compiler/com.sun.tools.javac.tree=ALL-UNNAMED --add-opens=jdk.compiler/com.sun.tools.javac.util=ALL-UNNAMED > "%GRADLE_USER_HOME%\gradle.properties"

echo org.gradle.parallel=true >> "%GRADLE_USER_HOME%\gradle.properties"
echo org.gradle.caching=true >> "%GRADLE_USER_HOME%\gradle.properties"
echo android.useAndroidX=true >> "%GRADLE_USER_HOME%\gradle.properties"
echo kotlin.code.style=official >> "%GRADLE_USER_HOME%\gradle.properties"

echo.
echo ✓ Created %GRADLE_USER_HOME%\gradle.properties
echo.
echo Configuration complete!
pause
