package com.rideconnect.rider.ui.ride

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
 * End-to-end UI tests for the complete ride request flow.
 * 
 * Tests cover:
 * - Location selection (pickup and dropoff)
 * - Fare estimation display
 * - Ride request confirmation
 * - Real-time ride tracking
 * - Driver details display
 * 
 * Requirements: 3.1, 3.2, 3.3, 3.5, 6.1, 6.2
 */
@HiltAndroidTest
@RunWith(AndroidJUnit4::class)
class RideRequestFlowTest {

    @get:Rule(order = 0)
    val hiltRule = HiltAndroidRule(this)

    @get:Rule(order = 1)
    val composeTestRule = createAndroidComposeRule<MainActivity>()

    @Before
    fun setup() {
        hiltRule.inject()
        // Assume user is already logged in for these tests
    }

    @Test
    fun testCompleteRideRequestFlow_fromLocationSelectionToTracking() {
        // Navigate to ride request screen
        composeTestRule
            .onNodeWithText("Request Ride")
            .performClick()

        // Wait for ride request screen
        composeTestRule.waitUntil(timeoutMillis = 5000) {
            composeTestRule
                .onAllNodesWithText("Where to?")
                .fetchSemanticsNodes().isNotEmpty()
        }

        // Select pickup location
        composeTestRule
            .onNodeWithTag("pickup_location_input")
            .performClick()

        composeTestRule
            .onNodeWithTag("pickup_location_input")
            .performTextInput("123 Main Street")

        // Select first suggestion
        composeTestRule
            .onNodeWithTag("location_suggestion_0")
            .performClick()

        // Select dropoff location
        composeTestRule
            .onNodeWithTag("dropoff_location_input")
            .performClick()

        composeTestRule
            .onNodeWithTag("dropoff_location_input")
            .performTextInput("456 Park Avenue")

        // Select first suggestion
        composeTestRule
            .onNodeWithTag("location_suggestion_0")
            .performClick()

        // Wait for fare estimate
        composeTestRule.waitUntil(timeoutMillis = 5000) {
            composeTestRule
                .onAllNodesWithTag("fare_estimate")
                .fetchSemanticsNodes().isNotEmpty()
        }

        // Verify fare estimate is displayed
        composeTestRule
            .onNodeWithTag("fare_estimate")
            .assertIsDisplayed()

        // Confirm ride request
        composeTestRule
            .onNodeWithText("Confirm Ride")
            .performClick()

        // Wait for ride matching
        composeTestRule.waitUntil(timeoutMillis = 10000) {
            composeTestRule
                .onAllNodesWithText("Finding driver...")
                .fetchSemanticsNodes().isNotEmpty()
        }

        // Wait for driver acceptance (simulated)
        composeTestRule.waitUntil(timeoutMillis = 15000) {
            composeTestRule
                .onAllNodesWithTag("driver_details")
                .fetchSemanticsNodes().isNotEmpty()
        }

        // Verify driver details are displayed
        composeTestRule
            .onNodeWithTag("driver_details")
            .assertIsDisplayed()

        // Verify tracking map is displayed
        composeTestRule
            .onNodeWithTag("tracking_map")
            .assertIsDisplayed()

        // Verify ETA is displayed
        composeTestRule
            .onNodeWithTag("driver_eta")
            .assertIsDisplayed()
    }

    @Test
    fun testRideRequest_withCurrentLocation_usesGPS() {
        // Navigate to ride request screen
        composeTestRule
            .onNodeWithText("Request Ride")
            .performClick()

        // Verify current location is set as pickup
        composeTestRule.waitUntil(timeoutMillis = 5000) {
            composeTestRule
                .onAllNodesWithTag("pickup_location_input")
                .fetchSemanticsNodes().isNotEmpty()
        }

        // Verify "Current Location" or GPS coordinates are displayed
        composeTestRule
            .onNodeWithTag("pickup_location_input")
            .assertTextContains("Current Location", substring = true, ignoreCase = true)
    }

    @Test
    fun testRideRequest_showsFareBreakdown() {
        // Navigate to ride request and select locations
        composeTestRule
            .onNodeWithText("Request Ride")
            .performClick()

        // Select locations (simplified)
        composeTestRule
            .onNodeWithTag("dropoff_location_input")
            .performTextInput("456 Park Avenue")

        composeTestRule
            .onNodeWithTag("location_suggestion_0")
            .performClick()

        // Wait for fare estimate
        composeTestRule.waitUntil(timeoutMillis = 5000) {
            composeTestRule
                .onAllNodesWithTag("fare_estimate")
                .fetchSemanticsNodes().isNotEmpty()
        }

        // Click on fare to see breakdown
        composeTestRule
            .onNodeWithTag("fare_estimate")
            .performClick()

        // Verify fare breakdown components
        composeTestRule
            .onNodeWithText("Base Fare")
            .assertIsDisplayed()

        composeTestRule
            .onNodeWithText("Distance")
            .assertIsDisplayed()

        composeTestRule
            .onNodeWithText("Time")
            .assertIsDisplayed()
    }

    @Test
    fun testRideTracking_displaysDriverLocation() {
        // Assume ride is already accepted
        // Navigate to tracking screen
        composeTestRule
            .onNodeWithTag("tracking_map")
            .assertIsDisplayed()

        // Verify driver marker is on map
        composeTestRule
            .onNodeWithTag("driver_marker")
            .assertIsDisplayed()

        // Verify route polyline is displayed
        composeTestRule
            .onNodeWithTag("route_polyline")
            .assertIsDisplayed()
    }

    @Test
    fun testRideRequest_outsideServiceRadius_showsError() {
        // Navigate to ride request screen
        composeTestRule
            .onNodeWithText("Request Ride")
            .performClick()

        // Enter location outside 20km radius
        composeTestRule
            .onNodeWithTag("dropoff_location_input")
            .performTextInput("Very Far Location, 100km away")

        composeTestRule
            .onNodeWithTag("location_suggestion_0")
            .performClick()

        // Verify error message
        composeTestRule.waitUntil(timeoutMillis = 5000) {
            composeTestRule
                .onAllNodesWithText("Location outside service area")
                .fetchSemanticsNodes().isNotEmpty()
        }
    }

    @Test
    fun testRideRequest_noDriverAvailable_showsRetryOption() {
        // Complete ride request
        composeTestRule
            .onNodeWithText("Request Ride")
            .performClick()

        // Select locations and confirm
        // ... (location selection code)

        composeTestRule
            .onNodeWithText("Confirm Ride")
            .performClick()

        // Wait for timeout (5 minutes simulated)
        composeTestRule.waitUntil(timeoutMillis = 10000) {
            composeTestRule
                .onAllNodesWithText("No driver available")
                .fetchSemanticsNodes().isNotEmpty()
        }

        // Verify retry and cancel options
        composeTestRule
            .onNodeWithText("Retry")
            .assertIsDisplayed()

        composeTestRule
            .onNodeWithText("Cancel")
            .assertIsDisplayed()
    }

    @Test
    fun testRideTracking_showsDriverArrivalNotification() {
        // Assume ride is in progress
        // Simulate driver arrival at pickup
        
        // Verify notification is displayed
        composeTestRule.waitUntil(timeoutMillis = 10000) {
            composeTestRule
                .onAllNodesWithText("Driver has arrived")
                .fetchSemanticsNodes().isNotEmpty()
        }

        composeTestRule
            .onNodeWithText("Driver has arrived")
            .assertIsDisplayed()
    }
}
