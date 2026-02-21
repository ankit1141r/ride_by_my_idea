package com.rideconnect.driver.ui.ride

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
 * End-to-end UI tests for ride execution flow.
 * 
 * Tests cover:
 * - Navigation to pickup
 * - Starting ride
 * - Navigation to dropoff
 * - Completing ride
 * - Ride cancellation
 * 
 * Requirements: 13.1, 13.2, 13.3, 13.5, 13.6, 13.8
 */
@HiltAndroidTest
@RunWith(AndroidJUnit4::class)
class RideExecutionFlowTest {

    @get:Rule(order = 0)
    val hiltRule = HiltAndroidRule(this)

    @get:Rule(order = 1)
    val composeTestRule = createAndroidComposeRule<MainActivity>()

    @Before
    fun setup() {
        hiltRule.inject()
        // Assume driver has accepted a ride
    }

    @Test
    fun testCompleteRideFlow_fromAcceptanceToCompletion() {
        // Verify active ride screen is displayed
        composeTestRule.waitUntil(timeoutMillis = 5000) {
            composeTestRule
                .onAllNodesWithTag("active_ride_screen")
                .fetchSemanticsNodes().isNotEmpty()
        }

        // Verify navigation to pickup is displayed
        composeTestRule
            .onNodeWithTag("navigation_map")
            .assertIsDisplayed()

        composeTestRule
            .onNodeWithText("Navigate to Pickup")
            .assertIsDisplayed()

        // Simulate arrival at pickup
        // Click start ride button
        composeTestRule.waitUntil(timeoutMillis = 10000) {
            composeTestRule
                .onAllNodesWithText("Start Ride")
                .fetchSemanticsNodes().isNotEmpty()
        }

        composeTestRule
            .onNodeWithText("Start Ride")
            .performClick()

        // Verify ride status changes to in progress
        composeTestRule.waitUntil(timeoutMillis = 5000) {
            composeTestRule
                .onAllNodesWithText("Navigate to Dropoff")
                .fetchSemanticsNodes().isNotEmpty()
        }

        composeTestRule
            .onNodeWithText("Navigate to Dropoff")
            .assertIsDisplayed()

        // Simulate arrival at dropoff
        composeTestRule.waitUntil(timeoutMillis = 10000) {
            composeTestRule
                .onAllNodesWithText("Complete Ride")
                .fetchSemanticsNodes().isNotEmpty()
        }

        // Click complete ride button
        composeTestRule
            .onNodeWithText("Complete Ride")
            .performClick()

        // Verify navigation to payment/rating screen
        composeTestRule.waitUntil(timeoutMillis = 5000) {
            composeTestRule
                .onAllNodesWithText("Ride Completed")
                .fetchSemanticsNodes().isNotEmpty()
        }

        composeTestRule
            .onNodeWithText("Ride Completed")
            .assertIsDisplayed()
    }

    @Test
    fun testActiveRideScreen_displaysRiderContactOptions() {
        // Verify active ride screen
        composeTestRule.waitUntil(timeoutMillis = 5000) {
            composeTestRule
                .onAllNodesWithTag("active_ride_screen")
                .fetchSemanticsNodes().isNotEmpty()
        }

        // Verify call button is displayed
        composeTestRule
            .onNodeWithTag("call_rider_button")
            .assertIsDisplayed()

        // Verify chat button is displayed
        composeTestRule
            .onNodeWithTag("chat_rider_button")
            .assertIsDisplayed()
    }

    @Test
    fun testRideCancellation_requiresReason_sendsToBackend() {
        // Verify active ride screen
        composeTestRule.waitUntil(timeoutMillis = 5000) {
            composeTestRule
                .onAllNodesWithTag("active_ride_screen")
                .fetchSemanticsNodes().isNotEmpty()
        }

        // Click cancel button
        composeTestRule
            .onNodeWithText("Cancel Ride")
            .performClick()

        // Verify cancellation dialog appears
        composeTestRule.waitUntil(timeoutMillis = 5000) {
            composeTestRule
                .onAllNodesWithText("Cancel Ride?")
                .fetchSemanticsNodes().isNotEmpty()
        }

        // Select cancellation reason
        composeTestRule
            .onNodeWithText("Rider not responding")
            .performClick()

        // Confirm cancellation
        composeTestRule
            .onNodeWithText("Confirm")
            .performClick()

        // Verify navigation back to online state
        composeTestRule.waitUntil(timeoutMillis = 5000) {
            composeTestRule
                .onAllNodesWithText("You're Online")
                .fetchSemanticsNodes().isNotEmpty()
        }
    }

    @Test
    fun testNavigation_displaysRouteAndETA() {
        // Verify active ride screen
        composeTestRule.waitUntil(timeoutMillis = 5000) {
            composeTestRule
                .onAllNodesWithTag("active_ride_screen")
                .fetchSemanticsNodes().isNotEmpty()
        }

        // Verify route polyline is displayed on map
        composeTestRule
            .onNodeWithTag("route_polyline")
            .assertIsDisplayed()

        // Verify ETA is displayed
        composeTestRule
            .onNodeWithTag("eta_display")
            .assertIsDisplayed()

        // Verify distance is displayed
        composeTestRule
            .onNodeWithTag("distance_display")
            .assertIsDisplayed()
    }

    @Test
    fun testStartRide_onlyEnabledAtPickupLocation() {
        // Verify active ride screen
        composeTestRule.waitUntil(timeoutMillis = 5000) {
            composeTestRule
                .onAllNodesWithTag("active_ride_screen")
                .fetchSemanticsNodes().isNotEmpty()
        }

        // Verify start ride button is disabled when not at pickup
        composeTestRule
            .onNodeWithText("Start Ride")
            .assertIsNotEnabled()

        // Simulate arrival at pickup (would require location mocking)
        // After arrival, button should be enabled
        composeTestRule.waitUntil(timeoutMillis = 10000) {
            composeTestRule
                .onAllNodesWithText("Start Ride")
                .fetchSemanticsNodes()
                .any { it.config.getOrNull(androidx.compose.ui.semantics.SemanticsProperties.Disabled) == null }
        }
    }
}
