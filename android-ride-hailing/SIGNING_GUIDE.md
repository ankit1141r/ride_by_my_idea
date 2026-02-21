# Android App Signing Guide

## Overview

This guide explains how to configure app signing for release builds of the Rider and Driver apps.

## Generate Keystores

### Rider App Keystore

```bash
keytool -genkey -v -keystore rider-release.keystore \
  -alias rider \
  -keyalg RSA \
  -keysize 2048 \
  -validity 10000
```

You'll be prompted for:
- Keystore password
- Key password
- Your name and organization details

### Driver App Keystore

```bash
keytool -genkey -v -keystore driver-release.keystore \
  -alias driver \
  -keyalg RSA \
  -keysize 2048 \
  -validity 10000
```

## Store Keystore Credentials Securely

### Option 1: Environment Variables (Recommended for CI/CD)

Set environment variables:
```bash
export RIDER_KEYSTORE_PASSWORD=your_keystore_password
export RIDER_KEY_PASSWORD=your_key_password
export DRIVER_KEYSTORE_PASSWORD=your_keystore_password
export DRIVER_KEY_PASSWORD=your_key_password
```

### Option 2: keystore.properties File (Local Development)

Create `keystore.properties` in project root:

```properties
# Rider App
rider.storeFile=../rider-release.keystore
rider.storePassword=your_keystore_password
rider.keyAlias=rider
rider.keyPassword=your_key_password

# Driver App
driver.storeFile=../driver-release.keystore
driver.storePassword=your_keystore_password
driver.keyAlias=driver
driver.keyPassword=your_key_password
```

**Important**: Add `keystore.properties` to `.gitignore` to prevent committing credentials!

## Configure Signing in Build Files

### Rider App (rider-app/build.gradle.kts)

Add before `android` block:

```kotlin
// Load keystore properties
val keystorePropertiesFile = rootProject.file("keystore.properties")
val keystoreProperties = Properties()
if (keystorePropertiesFile.exists()) {
    keystoreProperties.load(FileInputStream(keystorePropertiesFile))
}

android {
    // ... existing config ...
    
    signingConfigs {
        create("release") {
            storeFile = file(keystoreProperties["rider.storeFile"] as String? 
                ?: System.getenv("RIDER_KEYSTORE_FILE") 
                ?: "../rider-release.keystore")
            storePassword = keystoreProperties["rider.storePassword"] as String? 
                ?: System.getenv("RIDER_KEYSTORE_PASSWORD")
            keyAlias = keystoreProperties["rider.keyAlias"] as String? 
                ?: System.getenv("RIDER_KEY_ALIAS") 
                ?: "rider"
            keyPassword = keystoreProperties["rider.keyPassword"] as String? 
                ?: System.getenv("RIDER_KEY_PASSWORD")
        }
    }
    
    buildTypes {
        release {
            signingConfig = signingConfigs.getByName("release")
            // ... existing config ...
        }
    }
}
```

### Driver App (driver-app/build.gradle.kts)

Add before `android` block:

```kotlin
// Load keystore properties
val keystorePropertiesFile = rootProject.file("keystore.properties")
val keystoreProperties = Properties()
if (keystorePropertiesFile.exists()) {
    keystoreProperties.load(FileInputStream(keystorePropertiesFile))
}

android {
    // ... existing config ...
    
    signingConfigs {
        create("release") {
            storeFile = file(keystoreProperties["driver.storeFile"] as String? 
                ?: System.getenv("DRIVER_KEYSTORE_FILE") 
                ?: "../driver-release.keystore")
            storePassword = keystoreProperties["driver.storePassword"] as String? 
                ?: System.getenv("DRIVER_KEYSTORE_PASSWORD")
            keyAlias = keystoreProperties["driver.keyAlias"] as String? 
                ?: System.getenv("DRIVER_KEY_ALIAS") 
                ?: "driver"
            keyPassword = keystoreProperties["driver.keyPassword"] as String? 
                ?: System.getenv("DRIVER_KEY_PASSWORD")
        }
    }
    
    buildTypes {
        release {
            signingConfig = signingConfigs.getByName("release")
            // ... existing config ...
        }
    }
}
```

## Build Signed APKs

### Rider App

```bash
# Dev environment
./gradlew :rider-app:assembleDevRelease

# Staging environment
./gradlew :rider-app:assembleStagingRelease

# Production environment
./gradlew :rider-app:assembleProdRelease
```

APK location: `rider-app/build/outputs/apk/{flavor}/release/`

### Driver App

```bash
# Dev environment
./gradlew :driver-app:assembleDevRelease

# Staging environment
./gradlew :driver-app:assembleStagingRelease

# Production environment
./gradlew :driver-app:assembleProdRelease
```

APK location: `driver-app/build/outputs/apk/{flavor}/release/`

## Build App Bundles (for Google Play)

### Rider App

```bash
./gradlew :rider-app:bundleProdRelease
```

Bundle location: `rider-app/build/outputs/bundle/prodRelease/rider-app-prod-release.aab`

### Driver App

```bash
./gradlew :driver-app:bundleProdRelease
```

Bundle location: `driver-app/build/outputs/bundle/prodRelease/driver-app-prod-release.aab`

## Verify Signing

Check APK signature:

```bash
# For Rider App
jarsigner -verify -verbose -certs rider-app/build/outputs/apk/prod/release/rider-app-prod-release.apk

# For Driver App
jarsigner -verify -verbose -certs driver-app/build/outputs/apk/prod/release/driver-app-prod-release.apk
```

## CI/CD Configuration

### GitHub Actions Example

```yaml
name: Build Release APK

on:
  push:
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ubuntu-latest
    
    steps:
      - uses: actions/checkout@v3
      
      - name: Set up JDK 17
        uses: actions/setup-java@v3
        with:
          java-version: '17'
          distribution: 'temurin'
      
      - name: Decode Keystore
        run: |
          echo "${{ secrets.RIDER_KEYSTORE_BASE64 }}" | base64 -d > rider-release.keystore
          echo "${{ secrets.DRIVER_KEYSTORE_BASE64 }}" | base64 -d > driver-release.keystore
      
      - name: Build Rider App
        env:
          RIDER_KEYSTORE_FILE: ../rider-release.keystore
          RIDER_KEYSTORE_PASSWORD: ${{ secrets.RIDER_KEYSTORE_PASSWORD }}
          RIDER_KEY_ALIAS: rider
          RIDER_KEY_PASSWORD: ${{ secrets.RIDER_KEY_PASSWORD }}
        run: ./gradlew :rider-app:assembleProdRelease
      
      - name: Build Driver App
        env:
          DRIVER_KEYSTORE_FILE: ../driver-release.keystore
          DRIVER_KEYSTORE_PASSWORD: ${{ secrets.DRIVER_KEYSTORE_PASSWORD }}
          DRIVER_KEY_ALIAS: driver
          DRIVER_KEY_PASSWORD: ${{ secrets.DRIVER_KEY_PASSWORD }}
        run: ./gradlew :driver-app:assembleProdRelease
      
      - name: Upload Artifacts
        uses: actions/upload-artifact@v3
        with:
          name: release-apks
          path: |
            rider-app/build/outputs/apk/prod/release/*.apk
            driver-app/build/outputs/apk/prod/release/*.apk
```

### Required GitHub Secrets

1. `RIDER_KEYSTORE_BASE64`: Base64-encoded rider keystore
2. `RIDER_KEYSTORE_PASSWORD`: Rider keystore password
3. `RIDER_KEY_PASSWORD`: Rider key password
4. `DRIVER_KEYSTORE_BASE64`: Base64-encoded driver keystore
5. `DRIVER_KEYSTORE_PASSWORD`: Driver keystore password
6. `DRIVER_KEY_PASSWORD`: Driver key password

To encode keystore:
```bash
base64 -i rider-release.keystore | pbcopy  # macOS
base64 -w 0 rider-release.keystore         # Linux
```

## Security Best Practices

1. **Never commit keystores or passwords to version control**
   - Add `*.keystore` and `keystore.properties` to `.gitignore`

2. **Use different keystores for each app**
   - Rider and Driver apps should have separate keystores

3. **Store keystores securely**
   - Keep backups in secure, encrypted storage
   - Use password managers for credentials

4. **Rotate keys periodically**
   - Generate new keystores every 2-3 years
   - Update Google Play Console with new keys

5. **Use Play App Signing**
   - Let Google manage your app signing key
   - You only need to manage the upload key

## Troubleshooting

### "Keystore was tampered with, or password was incorrect"
- Verify keystore password is correct
- Check keystore file path is correct
- Ensure keystore file is not corrupted

### "Cannot find keystore file"
- Check file path in `keystore.properties`
- Ensure path is relative to project root
- Verify file exists at specified location

### "Key with alias 'rider' does not exist"
- Verify key alias is correct
- List aliases: `keytool -list -v -keystore rider-release.keystore`

## Additional Resources

- [Android App Signing Documentation](https://developer.android.com/studio/publish/app-signing)
- [Play App Signing](https://support.google.com/googleplay/android-developer/answer/9842756)
- [Gradle Signing Configuration](https://developer.android.com/studio/build/gradle-tips#sign-your-app)
