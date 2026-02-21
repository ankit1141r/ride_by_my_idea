package com.rideconnect.rider.ui.rating

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
 * End-to-end UI tests for the rating and review flow.
 * 
 * Tests cover:
 * - Rating submission after ride completion
 * - Star rating selection
 * - Review text input
 * - Rating validation
 * 
 * Requirements: 8.1, 8.2, 8.3, 8.4
 */
@HiltAndroidTest
@RunWith(AndroidJUnit4::class)
class RatingFlowTest {

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
    fun testCompleteRatingFlow_withStarAndReview_submitsSuccessfully() {
        // Wait for rating dialog to appear after ride completion
        composeTestRule.waitUntil(timeoutMillis = 5000) {
            composeTestRule
                .onAllNodesWithText("Rate your ride")
                .fetchSemanticsNodes().isNotEmpty()
        }

        // Select 5 stars
        composeTestRule
            .onNodeWithTag("star_5")
            .performClick()

        // Verify stars are selected
        composeTestRule
            .onNodeWithTag("star_5")
            .assertIsSelected()

        // Enter review text
        composeTestRule
            .onNodeWithTag("review_input")
            .performTextInput("Great driver, smooth ride!")

        // Submit rating
        composeTestRule
            .onNodeWithText("Submit")
            .performClick()

        // Verify success message
        composeTestRule.waitUntil(timeoutMillis = 5000) {
            composeTestRule
                .onAllNodesWithText("Thank you for your feedback")
                .fetchSemanticsNodes().isNotEmpty()
        }
    }

    @Test
    fun testRating_withoutStarSelection_showsError() {
        // Wait for rating dialog
        composeTestRule.waitUntil(timeoutMillis = 5000) {
            composeTestRule
                .onAllNodesWithText("Rate your ride")
                .fetchSemanticsNodes().isNotEmpty()
        }

        // Try to submit without selecting stars
        composeTestRule
            .onNodeWithText("Submit")
            .performClick()

        // Verify error message
        composeTestRule
            .onNodeWithText("Please select a rating")
            .assertIsDisplayed()
    }

    @Test
    fun testRating_reviewTextOptional_submitsWithoutReview() {
        // Wait for rating dialog
        composeTestRule.waitUntil(timeoutMillis = 5000) {
            composeTestRule
                .onAllNodesWithText("Rate your ride")
                .fetchSemanticsNodes().isNotEmpty()
        }

        // Select 4 stars
        composeTestRule
            .onNodeWithTag("star_4")
            .performClick()

        // Submit without review text
        composeTestRule
            .onNodeWithText("Submit")
            .performClick()

        // Verify submission succeeds
        composeTestRule.waitUntil(timeoutMillis = 5000) {
            composeTestRule
                .onAllNodesWithText("Thank you for your feedback")
                .fetchSemanticsNodes().isNotEmpty()
        }
    }

    @Test
    fun testRating_reviewTextExceedsLimit_showsError() {
        // Wait for rating dialog
        composeTestRule.waitUntil(timeoutMillis = 5000) {
            composeTestRule
                .onAllNodesWithText("Rate your ride")
                .fetchSemanticsNodes().isNotEmpty()
        }

        // Select stars
        composeTestRule
            .onNodeWithTag("star_5")
            .performClick()

        // Enter text exceeding 500 characters
        val longText = "a".repeat(501)
        composeTestRule
            .onNodeWithTag("review_input")
            .performTextInput(longText)

        // Verify character count error
        composeTestRule
            .onNodeWithText("Maximum 500 characters")
            .assertIsDisplayed()
    }

    @Test
    fun testRatingHistory_displaysAllPreviousRatings() {
        // Navigate to rating history
        composeTestRule
            .onNodeWithText("Profile")
            .performClick()

        composeTestRule
            .onNodeWithText("My Ratings")
            .performClick()

        // Wait for ratings to load
        composeTestRule.waitUntil(timeoutMillis = 5000) {
            composeTestRule
                .onAllNodesWithTag("rating_history_list")
                .fetchSemanticsNodes().isNotEmpty()
        }

        // Verify list is displayed
        composeTestRule
            .onNodeWithTag("rating_history_list")
            .assertIsDisplayed()

        // Verify rating items show stars and review
        composeTestRule
            .onNodeWithTag("rating_item_0")
            .assertIsDisplayed()
    }

    @Test
    fun testRating_canSkip_closesDialog() {
        // Wait for rating dialog
        composeTestRule.waitUntil(timeoutMillis = 5000) {
            composeTestRule
                .onAllNodesWithText("Rate your ride")
                .fetchSemanticsNodes().isNotEmpty()
        }

        // Click skip button
        composeTestRule
            .onNodeWithText("Skip")
            .performClick()

        // Verify dialog is closed
        composeTestRule
            .onNodeWithText("Rate your ride")
            .assertDoesNotExist()
    }

    @Test
    fun testRating_displaysDriverInfo() {
        // Wait for rating dialog
        composeTestRule.waitUntil(timeoutMillis = 5000) {
            composeTestRule
                .onAllNodesWithText("Rate your ride")
                .fetchSemanticsNodes().isNotEmpty()
        }

        // Verify driver name is displayed
        composeTestRule
            .onNodeWithTag("driver_name")
            .assertIsDisplayed()

        // Verify driver photo is displayed
        composeTestRule
            .onNodeWithTag("driver_photo")
            .assertIsDisplayed()
    }
}
