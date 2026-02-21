# Android Build Errors - Quick Fix Guide

## Common Build Errors and Solutions

### 1. JAVA_HOME Error
**Error**: `JAVA_HOME is set to an invalid directory`

**Solution**:
```batch
set JAVA_HOME=C:\Program Files\Java\jdk-21.0.10
```

Or in Android Studio:
- File → Settings → Build, Execution, Deployment → Build Tools → Gradle
- Set Gradle JDK to "jdk-21.0.10"

### 2. Missing Dependencies
**Error**: `Could not resolve` or `Failed to resolve`

**Solution**:
```batch
gradlew.bat clean build --refresh-dependencies
```

### 3. Kotlin Compilation Errors
**Error**: `Compilation error in :core:ui`

**Common Causes**:
- Missing imports
- Type mismatches
- Unresolved references

**Solution**: Please provide the specific error message from Android Studio's Build tab.

### 4. Sync Issues
**Error**: `Gradle sync failed`

**Solution**:
1. File → Invalidate Caches / Restart
2. Delete `.gradle` and `.idea` folders
3. Sync project again

### 5. Memory Issues
**Error**: `OutOfMemoryError` or `GC overhead limit exceeded`

**Solution**: Edit `gradle.properties`:
```properties
org.gradle.jvmargs=-Xmx4096m -XX:MaxMetaspaceSize=512m
```

## How to Get Detailed Error Information

### In Android Studio:
1. Click on "Build" tab at the bottom
2. Look for red error messages
3. Copy the complete error text including file names and line numbers

### From Command Line:
```batch
cd android-ride-hailing
set JAVA_HOME=C:\Program Files\Java\jdk-21.0.10
gradlew.bat assembleDebug --stacktrace > build_log.txt 2>&1
```

Then open `build_log.txt` and search for "error:"

## Next Steps

Please provide:
1. The exact error message from Android Studio's Build output
2. The file name and line number where the error occurs
3. Any red underlined code in the editor

This will help me provide a specific fix for your issue.
