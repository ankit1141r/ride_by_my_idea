# Security Configuration Guide

This document outlines the security features implemented in the RideConnect Android applications and how to configure them properly.

## Overview

The Android apps implement comprehensive security measures to protect user data and prevent attacks:

- **Encrypted Storage**: JWT tokens and sensitive data stored using EncryptedSharedPreferences
- **SSL Certificate Pinning**: Prevents man-in-the-middle attacks
- **Input Validation**: Prevents SQL injection and XSS attacks
- **Secure WebSocket**: Uses WSS protocol for real-time communication
- **Data Clearing**: Removes all sensitive data on logout
- **Code Obfuscation**: ProGuard configuration for release builds

## Requirements Addressed

- **24.1**: EncryptedSharedPreferences for JWT tokens
- **24.2**: SSL certificate pinning
- **24.3**: Input validation and sanitization
- **24.4**: Secure WebSocket connections (WSS)
- **24.5**: Clear sensitive data on logout
- **24.6**: ProGuard code obfuscation
- **24.7**: Remove debug logging in production
- **24.8**: Android Keystore for biometric keys

## 1. Encrypted Storage (Requirement 24.1, 24.8)

### Implementation

The `SecureStorageManager` class provides secure storage using:
- **EncryptedSharedPreferences** with AES256_GCM encryption
- **Android Keystore** for biometric authentication keys

### Usage

```kotlin
val secureStorageManager = SecureStorageManager(context)

// Create encrypted preferences
val prefs = secureStorageManager.createEncryptedPreferences("my_prefs")

// Generate biometric key
val key = secureStorageManager.generateBiometricKey("biometric_key")

// Clear encrypted data
secureStorageManager.clearEncryptedPreferences("my_prefs")
```

### Location

- `core/common/src/main/kotlin/com/rideconnect/core/common/security/SecureStorageManager.kt`
- `core/data/src/main/kotlin/com/rideconnect/core/data/local/TokenManager.kt`

## 2. SSL Certificate Pinning (Requirement 24.2)

### Implementation

Certificate pinning is configured in `CertificatePinnerConfig` and integrated into OkHttpClient.

### Configuration Steps

1. **Generate Certificate Pins**:

```bash
# Get certificate from server
openssl s_client -connect api.rideconnect.com:443 < /dev/null | openssl x509 -outform DER > cert.der

# Extract public key
openssl x509 -in cert.der -inform DER -pubkey -noout > pubkey.pem

# Generate SHA-256 hash
openssl pkey -pubin -in pubkey.pem -outform DER | openssl dgst -sha256 -binary | openssl enc -base64
```

2. **Update Certificate Pins**:

Edit `core/network/src/main/kotlin/com/rideconnect/core/network/security/CertificatePinner.kt`:

```kotlin
private val CERTIFICATE_PINS = arrayOf(
    "sha256/YOUR_PRIMARY_PIN_HERE",
    "sha256/YOUR_BACKUP_PIN_HERE"
)
```

3. **Best Practices**:
   - Always pin at least 2 certificates (primary + backup)
   - Update pins before certificate expiration
   - Test in staging environment first
   - Have a backup plan for pin updates

### Location

- `core/network/src/main/kotlin/com/rideconnect/core/network/security/CertificatePinner.kt`
- `core/network/src/main/kotlin/com/rideconnect/core/network/di/NetworkModule.kt`

## 3. Input Validation (Requirement 24.3)

### Implementation

The `InputValidator` object provides comprehensive input validation and sanitization.

### Features

- SQL injection prevention
- XSS attack prevention
- Phone number validation
- Email validation
- Coordinate validation
- File name sanitization

### Usage

```kotlin
// Sanitize text input
val sanitized = InputValidator.sanitizeTextInput(userInput)

// Validate phone number
if (InputValidator.isValidPhoneNumber(phone)) {
    // Process phone number
}

// Validate with detailed result
val result = InputValidator.validateProfileName(name)
if (result.isValid) {
    // Name is valid
} else {
    // Show error: result.errorMessage
}
```

### Location

- `core/common/src/main/kotlin/com/rideconnect/core/common/security/InputValidator.kt`

## 4. Secure WebSocket Connections (Requirement 24.4)

### Implementation

WebSocket connections use WSS (secure WebSocket) protocol in production.

### Configuration

The `WebSocketConfig` object manages WebSocket URLs:

```kotlin
// Get URL based on build type
val wsUrl = WebSocketConfig.getWebSocketUrl(BuildConfig.DEBUG)

// Development: ws://10.0.2.2:8000/ws
// Production: wss://api.rideconnect.com/ws
```

### Security Enforcement

The configuration enforces secure WebSocket in production:

```kotlin
val url = WebSocketConfig.enforceSecureWebSocket(url, isDebug)
// Throws SecurityException if using WS in production
```

### Location

- `core/network/src/main/kotlin/com/rideconnect/core/network/config/WebSocketConfig.kt`
- `core/data/src/main/kotlin/com/rideconnect/core/data/websocket/WebSocketManagerImpl.kt`

## 5. Data Clearing on Logout (Requirement 24.5)

### Implementation

The `DataCleaner` class handles comprehensive data clearing on logout.

### What Gets Cleared

- Authentication tokens (JWT access and refresh tokens)
- User profile data
- Biometric keys from Android Keystore
- Cached data in SharedPreferences
- In-memory sensitive data

### Usage

```kotlin
val dataCleaner = DataCleaner(context, secureStorageManager)

// Clear all sensitive data
dataCleaner.clearAllSensitiveData()

// Verify data was cleared
val isCleared = dataCleaner.verifySensitiveDataCleared()
```

### Integration

The `AuthRepository.logout()` method automatically calls `clearAll()` to remove tokens and user data.

### Location

- `core/common/src/main/kotlin/com/rideconnect/core/common/security/DataCleaner.kt`
- `core/data/src/main/kotlin/com/rideconnect/core/data/repository/AuthRepositoryImpl.kt`
- `core/data/src/main/kotlin/com/rideconnect/core/data/local/TokenManager.kt`

## 6. ProGuard Configuration (Requirement 24.6, 24.7)

### Implementation

ProGuard is configured for both Rider and Driver apps with:
- Aggressive code obfuscation
- Debug logging removal
- Security class obfuscation
- Third-party library rules

### Build Configuration

ProGuard is enabled in release builds:

```kotlin
buildTypes {
    release {
        isMinifyEnabled = true
        isShrinkResources = true
        proguardFiles(
            getDefaultProguardFile("proguard-android-optimize.txt"),
            "proguard-rules.pro"
        )
    }
}
```

### Debug Logging Removal

All debug logs are automatically removed in release builds:

```proguard
-assumenosideeffects class android.util.Log {
    public static *** d(...);
    public static *** v(...);
    public static *** i(...);
    public static *** w(...);
    public static *** e(...);
}

-assumenosideeffects class timber.log.Timber {
    public static *** d(...);
    public static *** v(...);
    public static *** i(...);
    public static *** w(...);
    public static *** e(...);
}
```

### Location

- `rider-app/proguard-rules.pro`
- `driver-app/proguard-rules.pro`
- `rider-app/build.gradle.kts`
- `driver-app/build.gradle.kts`

## Testing Security Features

### 1. Test Encrypted Storage

```kotlin
@Test
fun testTokenEncryption() {
    val token = AuthToken(...)
    tokenManager.saveToken(token)
    val retrieved = tokenManager.getToken()
    assertEquals(token, retrieved)
}
```

### 2. Test Certificate Pinning

Test with invalid certificate to ensure pinning works:
- Should throw `SSLPeerUnverifiedException`
- Should prevent connection to untrusted servers

### 3. Test Input Validation

```kotlin
@Test
fun testSqlInjectionPrevention() {
    val malicious = "'; DROP TABLE users; --"
    val sanitized = InputValidator.sanitizeSqlInput(malicious)
    assertFalse(sanitized.contains("DROP TABLE"))
}
```

### 4. Test Data Clearing

```kotlin
@Test
fun testDataClearingOnLogout() {
    // Save data
    tokenManager.saveToken(token)
    
    // Logout
    dataCleaner.clearAllSensitiveData()
    
    // Verify cleared
    assertNull(tokenManager.getToken())
    assertTrue(dataCleaner.verifySensitiveDataCleared())
}
```

## Production Checklist

Before releasing to production:

- [ ] Update SSL certificate pins with actual backend certificates
- [ ] Verify ProGuard rules don't break functionality
- [ ] Test certificate pinning with production server
- [ ] Verify all debug logs are removed in release build
- [ ] Test data clearing on logout
- [ ] Verify WebSocket uses WSS protocol
- [ ] Test input validation on all user inputs
- [ ] Verify encrypted storage is working
- [ ] Test biometric authentication
- [ ] Run security audit tools (e.g., MobSF)

## Security Best Practices

1. **Never hardcode secrets**: Use BuildConfig or remote config
2. **Rotate certificates regularly**: Update pins before expiration
3. **Monitor security logs**: Track failed authentication attempts
4. **Keep dependencies updated**: Regularly update security libraries
5. **Use HTTPS everywhere**: Never use HTTP in production
6. **Validate all inputs**: Never trust user input
7. **Minimize permissions**: Only request necessary permissions
8. **Use secure defaults**: Fail securely when errors occur

## Incident Response

If a security issue is discovered:

1. **Assess impact**: Determine what data may be compromised
2. **Patch immediately**: Deploy fix as soon as possible
3. **Notify users**: Inform affected users if necessary
4. **Rotate credentials**: Update certificates, API keys, etc.
5. **Review logs**: Check for signs of exploitation
6. **Update documentation**: Document the issue and fix

## References

- [Android Security Best Practices](https://developer.android.com/topic/security/best-practices)
- [OWASP Mobile Security](https://owasp.org/www-project-mobile-security/)
- [Android Keystore System](https://developer.android.com/training/articles/keystore)
- [Certificate Pinning](https://square.github.io/okhttp/4.x/okhttp/okhttp3/-certificate-pinner/)
