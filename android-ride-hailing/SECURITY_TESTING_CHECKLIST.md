# Security Testing Checklist

## Overview

This checklist guides you through security testing for the Android Ride-Hailing Application. Complete each test to ensure the app meets security requirements.

---

## 1. SSL Certificate Pinning

### Certificate Pinning Verification

**Steps:**
1. Configure a proxy (e.g., Charles Proxy, mitmproxy)
2. Install proxy certificate on device
3. Launch the app
4. Attempt to intercept HTTPS traffic

**Expected Result:**
- App should reject the connection
- Certificate pinning error should be logged
- No API calls should succeed through proxy

**Test Results:**
- [ ] Certificate pinning is active
- [ ] Proxy interception is blocked
- [ ] Error handling works correctly
- [ ] Document any issues: _____________________

### Certificate Validation Test

**Steps:**
1. Test with expired certificate (if possible in test environment)
2. Test with self-signed certificate
3. Test with wrong hostname

**Expected Results:**
- All invalid certificates should be rejected
- Clear error messages shown to user

**Test Results:**
- [ ] Expired certificates rejected
- [ ] Self-signed certificates rejected
- [ ] Hostname mismatch detected
- [ ] Document any issues: _____________________

---

## 2. Token Security

### Token Storage Verification

**Steps:**
1. Login to the app
2. Check token storage:
   ```bash
   adb shell run-as com.rideconnect.rider ls -la /data/data/com.rideconnect.rider/shared_prefs/
   ```
3. Verify tokens are in EncryptedSharedPreferences
4. Attempt to read the encrypted file

**Expected Results:**
- Tokens stored in encrypted preferences
- File content is encrypted (not readable)
- No tokens in plain SharedPreferences

**Test Results:**
- [ ] Tokens are encrypted
- [ ] No plain text tokens found
- [ ] EncryptedSharedPreferences is used
- [ ] Document any issues: _____________________

### Token Transmission Test

**Steps:**
1. Use network monitoring tool
2. Capture API requests
3. Verify token is in Authorization header
4. Verify HTTPS is used

**Expected Results:**
- Token sent in Authorization header
- All requests use HTTPS
- Token is JWT format

**Test Results:**
- [ ] Token in Authorization header
- [ ] HTTPS used for all requests
- [ ] Token format is correct
- [ ] Document any issues: _____________________

### Token Refresh Test

**Steps:**
1. Login to the app
2. Wait for token to expire (or manually expire it)
3. Make an API call
4. Verify automatic token refresh

**Expected Results:**
- 401 response triggers refresh
- New token obtained automatically
- Original request retried with new token
- User not logged out

**Test Results:**
- [ ] Token refresh works automatically
- [ ] Request succeeds after refresh
- [ ] No user interruption
- [ ] Document any issues: _____________________

### Token Expiration Test

**Steps:**
1. Login to the app
2. Manually set token expiration to past
3. Make an API call
4. Verify behavior

**Expected Results:**
- Expired token detected
- Refresh attempted
- If refresh fails, user logged out

**Test Results:**
- [ ] Expiration detected correctly
- [ ] Refresh attempted
- [ ] Logout on refresh failure
- [ ] Document any issues: _____________________

---

## 3. Data Encryption

### Sensitive Data Storage Test

**Steps:**
1. Login and use the app
2. Check all storage locations:
   ```bash
   adb shell run-as com.rideconnect.rider
   cd /data/data/com.rideconnect.rider
   find . -type f
   ```
3. Examine files for sensitive data

**Expected Results:**
- No plain text passwords
- No plain text tokens
- No unencrypted personal data
- Payment info not stored locally

**Test Results:**
- [ ] No plain text credentials found
- [ ] Personal data is encrypted
- [ ] Payment data not stored
- [ ] Document any issues: _____________________

### Database Encryption Test

**Steps:**
1. Locate the database file:
   ```bash
   adb shell run-as com.rideconnect.rider ls /data/data/com.rideconnect.rider/databases/
   ```
2. Pull the database:
   ```bash
   adb shell run-as com.rideconnect.rider cat /data/data/com.rideconnect.rider/databases/rideconnect.db > /sdcard/db.db
   adb pull /sdcard/db.db
   ```
3. Attempt to open with SQLite browser

**Expected Results:**
- Database should be encrypted (if encryption is enabled)
- Sensitive fields should not be readable

**Test Results:**
- [ ] Database encryption status: _____________________
- [ ] Sensitive data protection verified
- [ ] Document any issues: _____________________

### Biometric Key Storage Test

**Steps:**
1. Enable biometric authentication
2. Check Android Keystore:
   ```bash
   adb shell run-as com.rideconnect.rider
   ```
3. Verify biometric keys are in Keystore

**Expected Results:**
- Biometric keys stored in Android Keystore
- Keys are hardware-backed (if available)
- Keys cannot be extracted

**Test Results:**
- [ ] Keys in Android Keystore
- [ ] Hardware-backed: Yes/No
- [ ] Keys are secure
- [ ] Document any issues: _____________________

---

## 4. Input Validation

### SQL Injection Test

**Steps:**
1. Test input fields with SQL injection payloads:
   - `' OR '1'='1`
   - `'; DROP TABLE users; --`
   - `1' UNION SELECT * FROM users--`
2. Test in:
   - Search fields
   - Location input
   - Chat messages
   - Profile fields

**Expected Results:**
- All inputs sanitized
- No SQL errors
- Payloads treated as literal strings

**Test Results:**
- [ ] Search field: Protected
- [ ] Location input: Protected
- [ ] Chat messages: Protected
- [ ] Profile fields: Protected
- [ ] Document any issues: _____________________

### XSS/Script Injection Test

**Steps:**
1. Test input fields with script payloads:
   - `<script>alert('XSS')</script>`
   - `<img src=x onerror=alert('XSS')>`
   - `javascript:alert('XSS')`
2. Test in:
   - Profile name
   - Chat messages
   - Review text
   - Location names

**Expected Results:**
- Scripts not executed
- HTML tags escaped or stripped
- Content displayed safely

**Test Results:**
- [ ] Profile name: Protected
- [ ] Chat messages: Protected
- [ ] Review text: Protected
- [ ] Location names: Protected
- [ ] Document any issues: _____________________

### Path Traversal Test

**Steps:**
1. Test file-related inputs with path traversal:
   - `../../etc/passwd`
   - `..\..\windows\system32`
2. Test in:
   - Profile photo upload
   - Any file selection

**Expected Results:**
- Path traversal blocked
- Only allowed directories accessible
- File type validation works

**Test Results:**
- [ ] Path traversal blocked
- [ ] File type validation works
- [ ] Document any issues: _____________________

### Input Length Validation Test

**Steps:**
1. Test with extremely long inputs:
   - 10,000 character strings
   - Very long phone numbers
   - Oversized file uploads
2. Test in all input fields

**Expected Results:**
- Length limits enforced
- No crashes or freezes
- Clear error messages

**Test Results:**
- [ ] Length limits enforced
- [ ] App remains stable
- [ ] Error messages clear
- [ ] Document any issues: _____________________

### Special Character Handling Test

**Steps:**
1. Test with special characters:
   - Unicode characters (emoji, foreign scripts)
   - Control characters
   - Null bytes
2. Test in all input fields

**Expected Results:**
- Special characters handled safely
- No crashes or unexpected behavior
- Unicode displayed correctly

**Test Results:**
- [ ] Unicode handled correctly
- [ ] Control characters blocked
- [ ] Null bytes handled
- [ ] Document any issues: _____________________

---

## 5. WebSocket Security

### WSS Protocol Verification

**Steps:**
1. Monitor WebSocket connection
2. Verify WSS (secure WebSocket) is used
3. Check certificate validation

**Expected Results:**
- WSS protocol used (not WS)
- Certificate validated
- Encrypted connection

**Test Results:**
- [ ] WSS protocol confirmed
- [ ] Certificate validated
- [ ] Connection encrypted
- [ ] Document any issues: _____________________

### WebSocket Authentication Test

**Steps:**
1. Attempt to connect without token
2. Attempt to connect with invalid token
3. Attempt to connect with expired token
4. Connect with valid token

**Expected Results:**
- Connection rejected without token
- Connection rejected with invalid token
- Connection rejected with expired token
- Connection succeeds with valid token

**Test Results:**
- [ ] No token: Rejected
- [ ] Invalid token: Rejected
- [ ] Expired token: Rejected
- [ ] Valid token: Accepted
- [ ] Document any issues: _____________________

### Message Tampering Test

**Steps:**
1. Intercept WebSocket messages (if possible)
2. Attempt to modify message content
3. Send modified message

**Expected Results:**
- Modified messages rejected by server
- Or message integrity verified

**Test Results:**
- [ ] Message tampering detected
- [ ] Invalid messages rejected
- [ ] Document any issues: _____________________

---

## 6. Data Clearing on Logout

### Logout Data Clearing Test

**Steps:**
1. Login and use the app extensively
2. Logout
3. Check for remaining data:
   ```bash
   adb shell run-as com.rideconnect.rider
   cd /data/data/com.rideconnect.rider
   find . -type f -exec ls -lh {} \;
   ```

**Expected Results:**
- Auth tokens removed
- User data cleared from memory
- Cached sensitive data removed
- Database cleared or user data deleted

**Test Results:**
- [ ] Tokens removed
- [ ] Cache cleared
- [ ] Sensitive data removed
- [ ] Document remaining data: _____________________

### Memory Clearing Test

**Steps:**
1. Login to the app
2. Take memory dump:
   ```bash
   adb shell am dumpheap com.rideconnect.rider /sdcard/heap.hprof
   adb pull /sdcard/heap.hprof
   ```
3. Logout
4. Take another memory dump
5. Analyze for sensitive data

**Expected Results:**
- Sensitive data not in memory after logout
- Tokens cleared from memory

**Test Results:**
- [ ] Memory cleared after logout
- [ ] No tokens in memory dump
- [ ] Document any issues: _____________________

---

## 7. ProGuard/R8 Obfuscation

### Code Obfuscation Verification

**Steps:**
1. Build release APK
2. Decompile APK using jadx or similar:
   ```bash
   jadx -d output app-release.apk
   ```
3. Examine decompiled code

**Expected Results:**
- Class names obfuscated
- Method names obfuscated
- String constants protected
- Code flow obscured

**Test Results:**
- [ ] Classes obfuscated
- [ ] Methods obfuscated
- [ ] Strings protected
- [ ] Code is difficult to understand
- [ ] Document any issues: _____________________

### ProGuard Rules Verification

**Steps:**
1. Check proguard-rules.pro file
2. Verify critical classes are kept:
   - Data models
   - API interfaces
   - Parcelable classes
3. Build and test release APK

**Expected Results:**
- App functions correctly
- No crashes due to obfuscation
- Necessary classes preserved

**Test Results:**
- [ ] App functions correctly
- [ ] No obfuscation crashes
- [ ] Rules are appropriate
- [ ] Document any issues: _____________________

### Debug Logging Removal

**Steps:**
1. Build release APK
2. Run the app
3. Check logcat for debug logs:
   ```bash
   adb logcat | grep -i "rideconnect"
   ```

**Expected Results:**
- No debug logs in release build
- No sensitive information logged
- Only error logs present

**Test Results:**
- [ ] No debug logs found
- [ ] No sensitive data in logs
- [ ] Only appropriate logs present
- [ ] Document any issues: _____________________

---

## 8. Permission Security

### Permission Request Test

**Steps:**
1. Fresh install the app
2. Note which permissions are requested
3. Verify permissions are requested at appropriate times

**Expected Results:**
- Only necessary permissions requested
- Permissions requested when needed (not all at once)
- Clear rationale provided

**Test Results:**
- [ ] Only necessary permissions
- [ ] Appropriate timing
- [ ] Rationale provided
- [ ] Document any issues: _____________________

### Permission Denial Handling

**Steps:**
1. Deny each permission
2. Verify app handles denial gracefully
3. Test:
   - Location permission
   - Camera permission
   - Storage permission
   - Phone permission

**Expected Results:**
- App doesn't crash
- Clear error messages
- Functionality degrades gracefully

**Test Results:**
- [ ] Location denial: Handled
- [ ] Camera denial: Handled
- [ ] Storage denial: Handled
- [ ] Phone denial: Handled
- [ ] Document any issues: _____________________

---

## 9. API Security

### API Key Protection

**Steps:**
1. Decompile the APK
2. Search for API keys:
   - Google Maps API key
   - Firebase keys
   - Backend API keys
3. Check if keys are exposed

**Expected Results:**
- API keys not hardcoded in plain text
- Keys restricted by package name/signature
- Sensitive keys stored securely

**Test Results:**
- [ ] API keys protected
- [ ] Keys have restrictions
- [ ] Document any exposed keys: _____________________

### API Rate Limiting Test

**Steps:**
1. Make rapid API requests
2. Verify rate limiting works
3. Check error handling

**Expected Results:**
- Rate limiting enforced
- 429 errors handled gracefully
- Retry logic respects rate limits

**Test Results:**
- [ ] Rate limiting works
- [ ] Errors handled correctly
- [ ] Document any issues: _____________________

---

## 10. Third-Party Library Security

### Dependency Vulnerability Scan

**Steps:**
1. Run dependency check:
   ```bash
   ./gradlew dependencyCheckAnalyze
   ```
2. Review vulnerability report
3. Check for outdated libraries

**Expected Results:**
- No critical vulnerabilities
- Libraries are up to date
- Known vulnerabilities addressed

**Test Results:**
- [ ] No critical vulnerabilities
- [ ] Libraries up to date
- [ ] Document any issues: _____________________

---

## 11. Backup Security

### Backup Configuration Test

**Steps:**
1. Check AndroidManifest.xml for backup settings
2. Verify `android:allowBackup` configuration
3. Check backup rules

**Expected Results:**
- Backup disabled or properly configured
- Sensitive data excluded from backups
- Backup rules defined

**Test Results:**
- [ ] Backup configuration: _____________________
- [ ] Sensitive data excluded
- [ ] Document any issues: _____________________

---

## 12. Root Detection (Optional)

### Root Detection Test

**Steps:**
1. Test on rooted device (if available)
2. Verify app behavior
3. Check for root detection

**Expected Results:**
- App detects root (if implemented)
- Warning shown to user
- Security features may be disabled

**Test Results:**
- [ ] Root detection: Implemented/Not Implemented
- [ ] Behavior on rooted device: _____________________
- [ ] Document any issues: _____________________

---

## 13. Penetration Testing

### Manual Penetration Test

**Tools:**
- Burp Suite
- OWASP ZAP
- Frida
- Objection

**Test Areas:**
1. Authentication bypass attempts
2. Authorization checks
3. Session management
4. Data exposure
5. Business logic flaws

**Test Results:**
- [ ] Authentication: Secure
- [ ] Authorization: Secure
- [ ] Session management: Secure
- [ ] Data exposure: None found
- [ ] Business logic: Secure
- [ ] Document any vulnerabilities: _____________________

---

## Summary

### Security Rating

- [ ] **Excellent** - No vulnerabilities found
- [ ] **Good** - Minor issues only
- [ ] **Fair** - Some vulnerabilities need fixing
- [ ] **Poor** - Critical vulnerabilities found

### Critical Vulnerabilities Found

1. _____________________
2. _____________________
3. _____________________

### Recommendations

1. _____________________
2. _____________________
3. _____________________

### Compliance

- [ ] OWASP Mobile Top 10 reviewed
- [ ] Data protection requirements met
- [ ] Industry best practices followed

---

**Testing Date:** _____________________
**Tested By:** _____________________
**Tools Used:** _____________________
**Environment:** _____________________
