package com.rideconnect.rider.ui.auth

import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.test.ext.junit.runners.AndroidJUnit4
import com.rideconnect.rider.MainActivity
import dagger.hilt.android.testing.HiltAndroidRule
import dagger.hilt.android.testing.HiltAndroidTest
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

/**
 * End-to-end UI tests for the complete login flow in Rider App.
 * 
 * Tests cover:
 * - Phone number input and validation
 * - OTP verification
 * - Navigation to home screen after successful login
 * - Error handling for invalid inputs
 * 
 * Requirements: 1.1, 1.2, 1.6, 1.7
 */
@HiltAndroidTest
@RunWith(AndroidJUnit4::class)
class LoginFlowTest {

    @get:Rule(order = 0)
    val hiltRule = HiltAndroidRule(this)

    @get:Rule(order = 1)
    val composeTestRule = createAndroidComposeRule<MainActivity>()

    @Before
    fun setup() {
        hiltRule.inject()
    }

    @Test
    fun testCompleteLoginFlow_withValidCredentials_navigatesToHome() {
        // Wait for login screen to appear
        composeTestRule.waitUntil(timeoutMillis = 5000) {
            composeTestRule
                .onAllNodesWithText("Enter Phone Number")
                .fetchSemanticsNodes().isNotEmpty()
        }

        // Enter valid phone number
        composeTestRule
            .onNodeWithTag("phone_number_input")
            .performTextInput("+919876543210")

        // Click send OTP button
        composeTestRule
            .onNodeWithText("Send OTP")
            .performClick()

        // Wait for OTP screen
        composeTestRule.waitUntil(timeoutMillis = 5000) {
            composeTestRule
                .onAllNodesWithText("Enter OTP")
                .fetchSemanticsNodes().isNotEmpty()
        }

        // Enter OTP
        composeTestRule
            .onNodeWithTag("otp_input")
            .performTextInput("123456")

        // Click verify button
        composeTestRule
            .onNodeWithText("Verify")
            .performClick()

        // Verify navigation to home screen
        composeTestRule.waitUntil(timeoutMillis = 10000) {
            composeTestRule
                .onAllNodesWithText("Request Ride")
                .fetchSemanticsNodes().isNotEmpty()
        }

        composeTestRule
            .onNodeWithText("Request Ride")
            .assertIsDisplayed()
    }

    @Test
    fun testLoginFlow_withInvalidPhoneNumber_showsError() {
        // Wait for login screen
        composeTestRule.waitUntil(timeoutMillis = 5000) {
            composeTestRule
                .onAllNodesWithText("Enter Phone Number")
                .fetchSemanticsNodes().isNotEmpty()
        }

        // Enter invalid phone number
        composeTestRule
            .onNodeWithTag("phone_number_input")
            .performTextInput("123")

        // Click send OTP button
        composeTestRule
            .onNodeWithText("Send OTP")
            .performClick()

        // Verify error message is displayed
        composeTestRule
            .onNodeWithText("Invalid phone number format")
            .assertIsDisplayed()
    }

    @Test
    fun testOTPVerification_withInvalidOTP_showsError() {
        // Navigate to OTP screen (assuming we're already logged in or use test navigation)
        // Enter phone number
        composeTestRule
            .onNodeWithTag("phone_number_input")
            .performTextInput("+919876543210")

        composeTestRule
            .onNodeWithText("Send OTP")
            .performClick()

        // Wait for OTP screen
        composeTestRule.waitUntil(timeoutMillis = 5000) {
            composeTestRule
                .onAllNodesWithText("Enter OTP")
                .fetchSemanticsNodes().isNotEmpty()
        }

        // Enter invalid OTP
        composeTestRule
            .onNodeWithTag("otp_input")
            .performTextInput("000000")

        // Click verify button
        composeTestRule
            .onNodeWithText("Verify")
            .performClick()

        // Verify error message
        composeTestRule.waitUntil(timeoutMillis = 5000) {
            composeTestRule
                .onAllNodesWithText("Invalid OTP")
                .fetchSemanticsNodes().isNotEmpty()
        }
    }

    @Test
    fun testLoginScreen_displaysAllRequiredElements() {
        // Verify all UI elements are present
        composeTestRule
            .onNodeWithText("Enter Phone Number")
            .assertIsDisplayed()

        composeTestRule
            .onNodeWithTag("phone_number_input")
            .assertIsDisplayed()

        composeTestRule
            .onNodeWithText("Send OTP")
            .assertIsDisplayed()
    }

    @Test
    fun testNetworkError_duringLogin_showsRetryOption() {
        // This test would require mocking network failure
        // Enter phone number
        composeTestRule
            .onNodeWithTag("phone_number_input")
            .performTextInput("+919876543210")

        // Click send OTP (assuming network error is simulated)
        composeTestRule
            .onNodeWithText("Send OTP")
            .performClick()

        // Wait for error message
        composeTestRule.waitUntil(timeoutMillis = 5000) {
            composeTestRule
                .onAllNodesWithText("Network error")
                .fetchSemanticsNodes().isNotEmpty()
        }

        // Verify retry button is displayed
        composeTestRule
            .onNodeWithText("Retry")
            .assertIsDisplayed()
    }
}
