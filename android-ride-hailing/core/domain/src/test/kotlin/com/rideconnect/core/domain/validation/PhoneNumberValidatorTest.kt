package com.rideconnect.core.domain.validation

import io.kotest.core.spec.style.StringSpec
import io.kotest.matchers.shouldBe
import io.kotest.property.Arb
import io.kotest.property.arbitrary.string
import io.kotest.property.arbitrary.filter
import io.kotest.property.checkAll

/**
 * Property-Based Test for Phone Number Validation
 * 
 * Property 1: Phone Number Validation
 * Validates: Requirements 1.6
 * 
 * This test validates that phone number validation correctly identifies:
 * - Valid Indian phone numbers (+91 followed by 10 digits)
 * - Invalid formats (wrong length, missing country code, non-numeric characters)
 */
class PhoneNumberValidatorTest : StringSpec({
    
    "Property 1: Valid Indian phone numbers should pass validation" {
        checkAll(validIndianPhoneNumbers()) { phoneNumber ->
            PhoneNumberValidator.isValid(phoneNumber) shouldBe true
        }
    }
    
    "Property 1: Phone numbers with invalid length should fail validation" {
        checkAll(invalidLengthPhoneNumbers()) { phoneNumber ->
            PhoneNumberValidator.isValid(phoneNumber) shouldBe false
        }
    }
    
    "Property 1: Phone numbers without country code should fail validation" {
        checkAll(phoneNumbersWithoutCountryCode()) { phoneNumber ->
            PhoneNumberValidator.isValid(phoneNumber) shouldBe false
        }
    }
    
    "Property 1: Phone numbers with non-numeric characters should fail validation" {
        checkAll(phoneNumbersWithNonNumericChars()) { phoneNumber ->
            PhoneNumberValidator.isValid(phoneNumber) shouldBe false
        }
    }
    
    "Property 1: Phone numbers with invalid country code should fail validation" {
        checkAll(phoneNumbersWithInvalidCountryCode()) { phoneNumber ->
            PhoneNumberValidator.isValid(phoneNumber) shouldBe false
        }
    }
    
    "Property 1: Empty or blank phone numbers should fail validation" {
        PhoneNumberValidator.isValid("") shouldBe false
        PhoneNumberValidator.isValid("   ") shouldBe false
    }
})

// Generator for valid Indian phone numbers
private fun validIndianPhoneNumbers() = Arb.string(10..10)
    .filter { it.all { char -> char.isDigit() } }
    .filter { it.first() in '6'..'9' } // Indian mobile numbers start with 6-9
    .map { "+91$it" }

// Generator for phone numbers with invalid length
private fun invalidLengthPhoneNumbers() = Arb.string(1..20)
    .filter { it.length != 13 } // Valid format is +91 (3) + 10 digits = 13 chars
    .filter { it.all { char -> char.isDigit() || char == '+' } }

// Generator for phone numbers without country code
private fun phoneNumbersWithoutCountryCode() = Arb.string(10..10)
    .filter { it.all { char -> char.isDigit() } }
    .filter { it.first() in '6'..'9' }

// Generator for phone numbers with non-numeric characters
private fun phoneNumbersWithNonNumericChars() = Arb.string(13..13)
    .filter { str -> str.any { !it.isDigit() && it != '+' } }

// Generator for phone numbers with invalid country code
private fun phoneNumbersWithInvalidCountryCode() = Arb.string(10..10)
    .filter { it.all { char -> char.isDigit() } }
    .filter { it.first() in '6'..'9' }
    .map { number ->
        val invalidCodes = listOf("+1", "+44", "+86", "+81", "+61")
        "${invalidCodes.random()}$number"
    }
