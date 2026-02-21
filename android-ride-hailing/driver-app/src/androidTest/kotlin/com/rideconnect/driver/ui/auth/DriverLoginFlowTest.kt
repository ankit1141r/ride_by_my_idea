package com.rideconnect.driver.ui.auth

import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.createAndroidComposeRule
import androidx.test.ext.junit.runners.AndroidJUnit4
import com.rideconnect.driver.MainActivity
import dagger.hilt.android.testing.HiltAndroidRule
import dagger.hilt.android.testing.HiltAndroidTest
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import org.junit.runner.RunWith

/**
 * End-to-end UI tests for Driver App login flow.
 * 
 * Tests cover:
 * - Phone number input and validation
 * - OTP verification
 * - Navigation to driver home screen
 * 
 * Requirements: 1.1
 */
@HiltAndroidTest
@RunWith(AndroidJUnit4::class)
class DriverLoginFlowTest {

    @get:Rule(order = 0)
    val hiltRule = HiltAndroidRule(this)

    @get:Rule(order = 1)
    val composeTestRule = createAndroidComposeRule<MainActivity>()

    @Before
    fun setup() {
        hiltRule.inject()
    }

    @Test
    fun testDriverLoginFlow_withValidCredentials_navigatesToDriverHome() {
        // Wait for login screen
        composeTestRule.waitUntil(timeoutMillis = 5000) {
            composeTestRule
                .onAllNodesWithText("Enter Phone Number")
                .fetchSemanticsNodes().isNotEmpty()
        }

        // Enter phone number
        composeTestRule
            .onNodeWithTag("phone_number_input")
            .performTextInput("+919876543210")

        // Send OTP
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

        // Verify
        composeTestRule
            .onNodeWithText("Verify")
            .performClick()

        // Verify navigation to driver home
        composeTestRule.waitUntil(timeoutMillis = 10000) {
            composeTestRule
                .onAllNodesWithText("Go Online")
                .fetchSemanticsNodes().isNotEmpty()
        }

        composeTestRule
            .onNodeWithText("Go Online")
            .assertIsDisplayed()
    }
}
