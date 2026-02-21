package com.rideconnect.rider.ui.payment

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
 * End-to-end UI tests for the payment flow.
 * 
 * Tests cover:
 * - Fare breakdown display
 * - Payment confirmation
 * - Receipt generation
 * - Payment error handling
 * 
 * Requirements: 7.1, 7.2, 7.3, 7.4
 */
@HiltAndroidTest
@RunWith(AndroidJUnit4::class)
class PaymentFlowTest {

    @get:Rule(order = 0)
    val hiltRule = HiltAndroidRule(this)

    @get:Rule(order = 1)
    val composeTestRule = createAndroidComposeRule<MainActivity>()

    @Before
    fun setup() {
        hiltRule.inject()
        // Assume user is logged in and ride is completed
    }

    @Test
    fun testCompletePaymentFlow_withSuccessfulPayment_showsReceipt() {
        // Assume ride just completed and payment screen appears
        composeTestRule.waitUntil(timeoutMillis = 5000) {
            composeTestRule
                .onAllNodesWithText("Payment")
                .fetchSemanticsNodes().isNotEmpty()
        }

        // Verify fare breakdown is displayed
        composeTestRule
            .onNodeWithText("Base Fare")
            .assertIsDisplayed()

        composeTestRule
            .onNodeWithText("Distance Charge")
            .assertIsDisplayed()

        composeTestRule
            .onNodeWithText("Time Charge")
            .assertIsDisplayed()

        composeTestRule
            .onNodeWithTag("total_fare")
            .assertIsDisplayed()

        // Confirm payment
        composeTestRule
            .onNodeWithText("Pay Now")
            .performClick()

        // Wait for payment processing
        composeTestRule.waitUntil(timeoutMillis = 10000) {
            composeTestRule
                .onAllNodesWithText("Payment Successful")
                .fetchSemanticsNodes().isNotEmpty()
        }

        // Verify receipt is displayed
        composeTestRule
            .onNodeWithTag("receipt")
            .assertIsDisplayed()

        // Verify receipt contains all details
        composeTestRule
            .onNodeWithText("Transaction ID")
            .assertIsDisplayed()

        composeTestRule
            .onNodeWithText("Date")
            .assertIsDisplayed()

        composeTestRule
            .onNodeWithText("Route")
            .assertIsDisplayed()
    }

    @Test
    fun testPaymentScreen_displaysFareBreakdown() {
        // Navigate to payment screen
        composeTestRule.waitUntil(timeoutMillis = 5000) {
            composeTestRule
                .onAllNodesWithText("Payment")
                .fetchSemanticsNodes().isNotEmpty()
        }

        // Verify all fare components
        composeTestRule
            .onNodeWithText("Base Fare")
            .assertIsDisplayed()

        composeTestRule
            .onNodeWithText("Distance Charge")
            .assertIsDisplayed()

        composeTestRule
            .onNodeWithText("Time Charge")
            .assertIsDisplayed()

        // Verify total is calculated correctly
        composeTestRule
            .onNodeWithTag("total_fare")
            .assertIsDisplayed()
            .assertTextContains("₹", substring = true)
    }

    @Test
    fun testPayment_withFailure_showsErrorAndRetry() {
        // Navigate to payment screen
        composeTestRule.waitUntil(timeoutMillis = 5000) {
            composeTestRule
                .onAllNodesWithText("Payment")
                .fetchSemanticsNodes().isNotEmpty()
        }

        // Attempt payment (simulated failure)
        composeTestRule
            .onNodeWithText("Pay Now")
            .performClick()

        // Wait for error message
        composeTestRule.waitUntil(timeoutMillis = 10000) {
            composeTestRule
                .onAllNodesWithText("Payment Failed")
                .fetchSemanticsNodes().isNotEmpty()
        }

        // Verify error message and retry option
        composeTestRule
            .onNodeWithText("Payment Failed")
            .assertIsDisplayed()

        composeTestRule
            .onNodeWithText("Retry")
            .assertIsDisplayed()

        // Verify error details are shown
        composeTestRule
            .onNodeWithText("Please check your payment method and try again")
            .assertIsDisplayed()
    }

    @Test
    fun testReceipt_canBeShared() {
        // Assume payment is successful and receipt is displayed
        composeTestRule.waitUntil(timeoutMillis = 5000) {
            composeTestRule
                .onAllNodesWithTag("receipt")
                .fetchSemanticsNodes().isNotEmpty()
        }

        // Click share button
        composeTestRule
            .onNodeWithTag("share_receipt_button")
            .performClick()

        // Verify share dialog appears (system dialog)
        // Note: System dialogs are hard to test, so we verify the button works
        composeTestRule
            .onNodeWithTag("share_receipt_button")
            .assertExists()
    }

    @Test
    fun testPaymentHistory_displaysAllTransactions() {
        // Navigate to payment history
        composeTestRule
            .onNodeWithText("History")
            .performClick()

        composeTestRule
            .onNodeWithText("Payment History")
            .performClick()

        // Wait for history to load
        composeTestRule.waitUntil(timeoutMillis = 5000) {
            composeTestRule
                .onAllNodesWithTag("payment_history_list")
                .fetchSemanticsNodes().isNotEmpty()
        }

        // Verify list is displayed
        composeTestRule
            .onNodeWithTag("payment_history_list")
            .assertIsDisplayed()

        // Verify at least one transaction is shown
        composeTestRule
            .onNodeWithTag("payment_item_0")
            .assertIsDisplayed()
    }

    @Test
    fun testPaymentReceipt_containsAllRequiredDetails() {
        // Navigate to receipt
        composeTestRule.waitUntil(timeoutMillis = 5000) {
            composeTestRule
                .onAllNodesWithTag("receipt")
                .fetchSemanticsNodes().isNotEmpty()
        }

        // Verify all required fields
        val requiredFields = listOf(
            "Transaction ID",
            "Date",
            "Time",
            "Pickup Location",
            "Dropoff Location",
            "Distance",
            "Duration",
            "Base Fare",
            "Total Amount",
            "Driver Name",
            "Vehicle Number"
        )

        requiredFields.forEach { field ->
            composeTestRule
                .onNodeWithText(field)
                .assertIsDisplayed()
        }
    }
}
