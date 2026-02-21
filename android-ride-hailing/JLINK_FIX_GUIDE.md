# JDK/jlink Issue Fix Guide

## Problem Description

When building the Android project, you may encounter this error:

```
Execution failed for task ':core:database:compileDebugJavaWithJavac'.
> Could not resolve all files for configuration ':core:database:androidJdkImage'.
  > Failed to transform core-for-system-modules.jar to match attributes
    > Error while executing process C:\Program Files\Android\Android Studio\jbr\bin\jlink.exe
```

## Root Cause

This is a known issue with Android Gradle Plugin 8.2.0 and certain JDK configurations. The jlink tool (part of the JDK) fails when trying to create a JDK image for Android compilation. This typically happens due to:

1. Corrupted Gradle cache
2. Incompatibility between AGP version and JDK version
3. Issues with the jlink tool in the bundled JDK

## Solution

### Quick Fix (Recommended)

Run the provided batch script:

```batch
cd android-ride-hailing
fix_jlink_issue.bat
```

This script will:
1. Stop the Gradle daemon
2. Clear the transforms cache
3. Clear the jars cache
4. Clear the build cache
5. Clean project build directories

After running the script, try building again:

```batch
gradlew.bat assembleDebug
```

### Manual Fix

If the script doesn't work, follow these manual steps:

#### Step 1: Stop Gradle Daemon
```batch
gradlew.bat --stop
```

#### Step 2: Clear Gradle Caches
```batch
rmdir /s /q "%USERPROFILE%\.gradle\caches\transforms-3"
rmdir /s /q "%USERPROFILE%\.gradle\caches\jars-*"
rmdir /s /q "%USERPROFILE%\.gradle\caches\build-cache-*"
```

#### Step 3: Clean Project
```batch
gradlew.bat clean
```

#### Step 4: Rebuild
```batch
gradlew.bat assembleDebug
```

### Alternative Solutions

If the above doesn't work, try these alternatives:

#### Option 1: Update Android Gradle Plugin

Update `build.gradle.kts` to use a newer AGP version:

```kotlin
plugins {
    id("com.android.application") version "8.3.0" apply false
    id("com.android.library") version "8.3.0" apply false
    // ... other plugins
}
```

#### Option 2: Use a Different JDK

If you have multiple JDKs installed, try using a different one:

1. Open Android Studio
2. Go to File → Settings → Build, Execution, Deployment → Build Tools → Gradle
3. Change "Gradle JDK" to a different version (preferably JDK 17)

#### Option 3: Disable Parallel Builds Temporarily

In `gradle.properties`, temporarily disable parallel builds:

```properties
org.gradle.parallel=false
```

## Configuration Changes Applied

The following changes have been made to `gradle.properties` to prevent this issue:

```properties
# Disable configuration cache (can cause jlink issues)
org.gradle.configuration-cache=false

# Disable compile SDK checks (workaround for jlink issues)
android.experimental.disableCompileSdkChecks=true
```

## Verification

After applying the fix, verify the build works:

```batch
# Clean build
gradlew.bat clean

# Build debug variant
gradlew.bat assembleDebug

# If successful, you should see:
# BUILD SUCCESSFUL in Xm Ys
```

## Prevention

To prevent this issue in the future:

1. **Keep Gradle updated**: Regularly update to the latest stable Gradle version
2. **Clear caches periodically**: Run `gradlew.bat clean` before major builds
3. **Use stable JDK versions**: Stick to LTS JDK versions (11, 17, 21)
4. **Avoid configuration cache**: Keep it disabled if you encounter issues

## Additional Resources

- [Android Gradle Plugin Release Notes](https://developer.android.com/studio/releases/gradle-plugin)
- [Gradle Build Cache](https://docs.gradle.org/current/userguide/build_cache.html)
- [JDK Compatibility](https://developer.android.com/studio/releases#jdk-compatibility)

## Troubleshooting

### Issue: Script doesn't fix the problem

**Solution**: Try deleting the entire `.gradle` folder in your user directory:
```batch
rmdir /s /q "%USERPROFILE%\.gradle"
```
⚠️ Warning: This will delete all Gradle caches and you'll need to re-download dependencies.

### Issue: Build still fails with jlink error

**Solution**: Check your JDK installation:
1. Verify JDK 17 is installed: `java -version`
2. Ensure JAVA_HOME is set correctly
3. Try using Android Studio's embedded JDK

### Issue: Out of memory errors

**Solution**: Increase Gradle memory in `gradle.properties`:
```properties
org.gradle.jvmargs=-Xmx4096m -Dfile.encoding=UTF-8
```

## Contact

If you continue to experience issues after trying all solutions, please:
1. Check the Android Studio logs
2. Review the full error stack trace
3. Verify your environment setup (JDK, Android SDK, etc.)
