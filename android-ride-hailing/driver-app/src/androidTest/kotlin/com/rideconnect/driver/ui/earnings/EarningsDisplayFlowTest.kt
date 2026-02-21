package com.rideconnect.driver.ui.earnings

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
 * End-to-end UI tests for earnings tracking and display.
 * 
 * Tests cover:
 * - Earnings display on dashboard
 * - Earnings breakdown by period
 * - Ride completion updates earnings
 * - Statistics display
 * 
 * Requirements: 14.1, 14.2, 14.3, 14.4
 */
@HiltAndroidTest
@RunWith(AndroidJUnit4::class)
class EarningsDisplayFlowTest {

    @get:Rule(order = 0)
    val hiltRule = HiltAndroidRule(this)

    @get:Rule(order = 1)
    val composeTestRule = createAndroidComposeRule<MainActivity>()

    @Before
    fun setup() {
        hiltRule.inject()
        // Assume driver is logged in
    }

    @Test
    fun testDashboard_displaysTodaysEarnings() {
        // Wait for driver home screen
        composeTestRule.waitUntil(timeoutMillis = 5000) {
            composeTestRule
                .onAllNodesWithTag("driver_home_screen")
                .fetchSemanticsNodes().isNotEmpty()
        }

        // Verify today's earnings are displayed
        composeTestRule
            .onNodeWithTag("todays_earnings")
            .assertIsDisplayed()

        // Verify earnings amount is displayed
        composeTestRule
            .onNodeWithTag("earnings_amount")
            .assertIsDisplayed()
            .assertTextContains("₹", substring = true)
    }

    @Test
    fun testEarningsScreen_showsBreakdownByPeriod() {
        // Navigate to earnings screen
        composeTestRule
            .onNodeWithText("Earnings")
            .performClick()

        // Wait for earnings screen
        composeTestRule.waitUntil(timeoutMillis = 5000) {
            composeTestRule
                .onAllNodesWithTag("earnings_screen")
                .fetchSemanticsNodes().isNotEmpty()
        }

        // Verify period tabs are displayed
        composeTestRule
            .onNodeWithText("Day")
            .assertIsDisplayed()

        composeTestRule
            .onNodeWithText("Week")
            .assertIsDisplayed()

        composeTestRule
            .onNodeWithText("Month")
            .assertIsDisplayed()

        // Click on week tab
        composeTestRule
            .onNodeWithText("Week")
            .performClick()

        // Verify weekly earnings are displayed
        composeTestRule
            .onNodeWithTag("weekly_earnings")
            .assertIsDisplayed()
    }

    @Test
    fun testEarningsScreen_displaysStatistics() {
        // Navigate to earnings screen
        composeTestRule
            .onNodeWithText("Earnings")
            .performClick()

        // Wait for earnings screen
        composeTestRule.waitUntil(timeoutMillis = 5000) {
            composeTestRule
                .onAllNodesWithTag("earnings_screen")
                .fetchSemanticsNodes().isNotEmpty()
        }

        // Verify statistics are displayed
        composeTestRule
            .onNodeWithText("Total Rides")
            .assertIsDisplayed()

        composeTestRule
            .onNodeWithText("Average Fare")
            .assertIsDisplayed()

        composeTestRule
            .onNodeWithText("Total Earnings")
            .assertIsDisplayed()
    }

    @Test
    fun testEarnings_updateAfterRideCompletion() {
        // Note initial earnings
        val initialEarnings = composeTestRule
            .onNodeWithTag("todays_earnings")
            .fetchSemanticsNode()
            .config[androidx.compose.ui.semantics.SemanticsProperties.Text]
            .first()
            .text

        // Complete a ride (simulated)
        // ... ride completion flow ...

        // Verify earnings are updated
        composeTestRule.waitUntil(timeoutMillis = 5000) {
            val currentEarnings = composeTestRule
                .onNodeWithTag("todays_earnings")
                .fetchSemanticsNode()
                .config[androidx.compose.ui.semantics.SemanticsProperties.Text]
                .first()
                .text
            
            currentEarnings != initialEarnings
        }
    }

    @Test
    fun testEarningsScreen_displaysRideList() {
        // Navigate to earnings screen
        composeTestRule
            .onNodeWithText("Earnings")
            .performClick()

        // Wait for earnings screen
        composeTestRule.waitUntil(timeoutMillis = 5000) {
            composeTestRule
                .onAllNodesWithTag("earnings_screen")
                .fetchSemanticsNodes().isNotEmpty()
        }

        // Verify ride list is displayed
        composeTestRule
            .onNodeWithTag("ride_list")
            .assertIsDisplayed()

        // Verify at least one ride item is shown
        composeTestRule
            .onNodeWithTag("ride_item_0")
            .assertIsDisplayed()

        // Verify ride item shows fare
        composeTestRule
            .onNodeWithTag("ride_item_0")
            .assertTextContains("₹", substring = true)
    }

    @Test
    fun testEarningsScreen_displaysPendingEarnings() {
        // Navigate to earnings screen
        composeTestRule
            .onNodeWithText("Earnings")
            .performClick()

        // Wait for earnings screen
        composeTestRule.waitUntil(timeoutMillis = 5000) {
            composeTestRule
                .onAllNodesWithTag("earnings_screen")
                .fetchSemanticsNodes().isNotEmpty()
        }

        // Verify pending earnings section
        composeTestRule
            .onNodeWithText("Pending")
            .assertIsDisplayed()

        composeTestRule
            .onNodeWithTag("pending_earnings")
            .assertIsDisplayed()
    }
}
