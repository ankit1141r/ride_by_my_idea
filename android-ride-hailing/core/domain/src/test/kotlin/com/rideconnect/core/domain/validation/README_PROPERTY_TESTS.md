# Property-Based Testing for Phone Number Validation

## Overview

This directory contains property-based tests (PBT) for the phone number validation logic. Property-based testing validates universal properties that should hold true for all inputs, rather than testing specific examples.

## Property 1: Phone Number Validation

**Validates**: Requirements 1.6 - Phone number format validation

### What is Being Tested

The phone number validator must correctly identify valid and invalid Indian mobile phone numbers according to these rules:

**Valid Format:**
- Must start with `+91` (India country code)
- Followed by exactly 10 digits
- First digit must be 6, 7, 8, or 9 (Indian mobile number range)
- No spaces or special characters except the leading `+`

**Examples:**
- ✅ Valid: `+919876543210`
- ✅ Valid: `+916123456789`
- ❌ Invalid: `9876543210` (missing country code)
- ❌ Invalid: `+91123456789` (starts with 1, not 6-9)
- ❌ Invalid: `+9198765432` (only 9 digits)
- ❌ Invalid: `+9198765432101` (11 digits)
- ❌ Invalid: `+91 9876543210` (contains space)

### Properties Tested

1. **Valid Indian Phone Numbers**: All phone numbers matching the pattern `+91[6-9]XXXXXXXXX` should pass validation
2. **Invalid Length**: Phone numbers with length != 13 characters should fail
3. **Missing Country Code**: Phone numbers without `+91` prefix should fail
4. **Non-Numeric Characters**: Phone numbers containing letters or special chars (except leading +) should fail
5. **Invalid Country Code**: Phone numbers with country codes other than +91 should fail
6. **Empty/Blank**: Empty or whitespace-only strings should fail

### Test Generators

The test uses Kotest's property-based testing framework with custom generators:

- `validIndianPhoneNumbers()`: Generates valid +91 phone numbers
- `invalidLengthPhoneNumbers()`: Generates numbers with wrong length
- `phoneNumbersWithoutCountryCode()`: Generates 10-digit numbers without +91
- `phoneNumbersWithNonNumericChars()`: Generates numbers with invalid characters
- `phoneNumbersWithInvalidCountryCode()`: Generates numbers with wrong country codes

### Running the Tests

```bash
# Run all tests in the domain module
./gradlew :core:domain:test

# Run only property tests
./gradlew :core:domain:test --tests "*PhoneNumberValidatorTest"

# Run with detailed output
./gradlew :core:domain:test --tests "*PhoneNumberValidatorTest" --info
```

### Test Configuration

- **Framework**: Kotest 5.8.0
- **Test Style**: StringSpec (descriptive test names)
- **Iterations**: Default 1000 iterations per property (configurable)
- **Shrinking**: Automatic shrinking to find minimal failing case

### Why Property-Based Testing?

Traditional unit tests check specific examples:
```kotlin
// Traditional test
"valid phone number" {
    isValid("+919876543210") shouldBe true
}
```

Property-based tests check universal properties across thousands of generated inputs:
```kotlin
// Property test
"all valid Indian phone numbers should pass" {
    checkAll(validIndianPhoneNumbers()) { phoneNumber ->
        isValid(phoneNumber) shouldBe true
    }
}
```

This approach:
- Tests edge cases you might not think of
- Validates the property holds for ALL valid inputs
- Automatically finds minimal failing examples (shrinking)
- Provides higher confidence in correctness

### Integration with Requirements

This test directly validates **Requirement 1.6**:
> "WHEN a user enters an invalid phone number format THEN the app SHALL display a validation error before sending to backend"

By ensuring the validator correctly identifies all invalid formats, we prevent invalid data from reaching the backend, improving user experience and reducing unnecessary API calls.

### Maintenance Notes

- If phone number format requirements change, update both the validator and test generators
- Consider adding generators for international formats if expanding beyond India
- Monitor test execution time - property tests run many iterations
- Failed tests will show the minimal failing example for easy debugging
