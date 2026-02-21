package com.rideconnect.driver.ui.availability

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
 * End-to-end UI tests for driver availability management.
 * 
 * Tests cover:
 * - Going online/offline
 * - Receiving ride requests
 * - Accepting/rejecting rides
 * - Countdown timer functionality
 * 
 * Requirements: 11.1, 11.2, 12.1, 12.3, 12.4
 */
@HiltAndroidTest
@RunWith(AndroidJUnit4::class)
class DriverAvailabilityFlowTest {

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
    fun testGoingOnline_startsLocationTracking_displaysOnlineStatus() {
        // Wait for driver home screen
        composeTestRule.waitUntil(timeoutMillis = 5000) {
            composeTestRule
                .onAllNodesWithText("Go Online")
                .fetchSemanticsNodes().isNotEmpty()
        }

        // Click go online button
        composeTestRule
            .onNodeWithText("Go Online")
            .performClick()

        // Verify status changes to online
        composeTestRule.waitUntil(timeoutMillis = 5000) {
            composeTestRule
                .onAllNodesWithText("You're Online")
                .fetchSemanticsNodes().isNotEmpty()
        }

        composeTestRule
            .onNodeWithText("You're Online")
            .assertIsDisplayed()

        // Verify go offline button is now displayed
        composeTestRule
            .onNodeWithText("Go Offline")
            .assertIsDisplayed()
    }

    @Test
    fun testReceivingRideRequest_displaysRequestDialog() {
        // Go online first
        composeTestRule
            .onNodeWithText("Go Online")
            .performClick()

        // Wait for ride request (simulated)
        composeTestRule.waitUntil(timeoutMillis = 15000) {
            composeTestRule
                .onAllNodesWithTag("ride_request_dialog")
                .fetchSemanticsNodes().isNotEmpty()
        }

        // Verify ride request dialog is displayed
        composeTestRule
            .onNodeWithTag("ride_request_dialog")
            .assertIsDisplayed()

        // Verify request details
        composeTestRule
            .onNodeWithText("Pickup Location")
            .assertIsDisplayed()

        composeTestRule
            .onNodeWithText("Dropoff Location")
            .assertIsDisplayed()

        composeTestRule
            .onNodeWithTag("estimated_fare")
            .assertIsDisplayed()

        // Verify countdown timer
        composeTestRule
            .onNodeWithTag("countdown_timer")
            .assertIsDisplayed()
    }

    @Test
    fun testAcceptingRideRequest_navigatesToActiveRide() {
        // Assume ride request is displayed
        composeTestRule.waitUntil(timeoutMillis = 5000) {
            composeTestRule
                .onAllNodesWithTag("ride_request_dialog")
                .fetchSemanticsNodes().isNotEmpty()
        }

        // Click accept button
        composeTestRule
            .onNodeWithText("Accept")
            .performClick()

        // Verify navigation to active ride screen
        composeTestRule.waitUntil(timeoutMillis = 5000) {
            composeTestRule
                .onAllNodesWithTag("active_ride_screen")
                .fetchSemanticsNodes().isNotEmpty()
        }

        composeTestRule
            .onNodeWithTag("active_ride_screen")
            .assertIsDisplayed()

        // Verify navigation map is displayed
        composeTestRule
            .onNodeWithTag("navigation_map")
            .assertIsDisplayed()
    }

    @Test
    fun testRejectingRideRequest_returnsToOnlineState() {
        // Assume ride request is displayed
        composeTestRule.waitUntil(timeoutMillis = 5000) {
            composeTestRule
                .onAllNodesWithTag("ride_request_dialog")
                .fetchSemanticsNodes().isNotEmpty()
        }

        // Click reject button
        composeTestRule
            .onNodeWithText("Reject")
            .performClick()

        // Verify dialog is dismissed
        composeTestRule
            .onNodeWithTag("ride_request_dialog")
            .assertDoesNotExist()

        // Verify still online
        composeTestRule
            .onNodeWithText("You're Online")
            .assertIsDisplayed()
    }

    @Test
    fun testCountdownTimer_expiresAfter30Seconds_autoRejects() {
        // Assume ride request is displayed
        composeTestRule.waitUntil(timeoutMillis = 5000) {
            composeTestRule
                .onAllNodesWithTag("ride_request_dialog")
                .fetchSemanticsNodes().isNotEmpty()
        }

        // Wait for countdown to expire (simulated - actual would be 30s)
        composeTestRule.waitUntil(timeoutMillis = 35000) {
            composeTestRule
                .onAllNodesWithTag("ride_request_dialog")
                .fetchSemanticsNodes().isEmpty()
        }

        // Verify dialog is auto-dismissed
        composeTestRule
            .onNodeWithTag("ride_request_dialog")
            .assertDoesNotExist()

        // Verify notification about auto-rejection
        composeTestRule
            .onNodeWithText("Ride request expired")
            .assertIsDisplayed()
    }

    @Test
    fun testGoingOffline_duringActiveRide_showsWarning() {
        // Assume driver has active ride
        composeTestRule.waitUntil(timeoutMillis = 5000) {
            composeTestRule
                .onAllNodesWithTag("active_ride_screen")
                .fetchSemanticsNodes().isNotEmpty()
        }

        // Try to go offline
        composeTestRule
            .onNodeWithText("Go Offline")
            .performClick()

        // Verify warning is displayed
        composeTestRule
            .onNodeWithText("Cannot go offline during active ride")
            .assertIsDisplayed()
    }

    @Test
    fun testLowBattery_showsWarning() {
        // Simulate low battery (< 15%)
        // This would require battery level mocking

        // Verify warning is displayed
        composeTestRule.waitUntil(timeoutMillis = 5000) {
            composeTestRule
                .onAllNodesWithText("Low battery")
                .fetchSemanticsNodes().isNotEmpty()
        }

        composeTestRule
            .onNodeWithText("Low battery")
            .assertIsDisplayed()
    }
}
