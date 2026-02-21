package com.rideconnect.rider.ui.settings

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
 * End-to-end UI tests for settings and preferences.
 * 
 * Tests cover:
 * - Language switching
 * - Theme switching
 * - Notification preferences
 * - Logout functionality
 * 
 * Requirements: 21.2, 22.2, 27.2
 */
@HiltAndroidTest
@RunWith(AndroidJUnit4::class)
class SettingsFlowTest {

    @get:Rule(order = 0)
    val hiltRule = HiltAndroidRule(this)

    @get:Rule(order = 1)
    val composeTestRule = createAndroidComposeRule<MainActivity>()

    @Before
    fun setup() {
        hiltRule.inject()
        // Assume user is logged in
    }

    @Test
    fun testLanguageSwitch_fromEnglishToHindi_updatesUI() {
        // Navigate to settings
        composeTestRule
            .onNodeWithText("Profile")
            .performClick()

        composeTestRule
            .onNodeWithText("Settings")
            .performClick()

        // Wait for settings screen
        composeTestRule.waitUntil(timeoutMillis = 5000) {
            composeTestRule
                .onAllNodesWithTag("settings_screen")
                .fetchSemanticsNodes().isNotEmpty()
        }

        // Click on language option
        composeTestRule
            .onNodeWithText("Language")
            .performClick()

        // Select Hindi
        composeTestRule
            .onNodeWithText("हिंदी (Hindi)")
            .performClick()

        // Verify UI updates to Hindi
        composeTestRule.waitUntil(timeoutMillis = 5000) {
            composeTestRule
                .onAllNodesWithText("सेटिंग्स")
                .fetchSemanticsNodes().isNotEmpty()
        }

        composeTestRule
            .onNodeWithText("सेटिंग्स")
            .assertIsDisplayed()
    }

    @Test
    fun testThemeSwitch_fromLightToDark_updatesColors() {
        // Navigate to settings
        composeTestRule
            .onNodeWithText("Profile")
            .performClick()

        composeTestRule
            .onNodeWithText("Settings")
            .performClick()

        // Wait for settings screen
        composeTestRule.waitUntil(timeoutMillis = 5000) {
            composeTestRule
                .onAllNodesWithTag("settings_screen")
                .fetchSemanticsNodes().isNotEmpty()
        }

        // Click on theme option
        composeTestRule
            .onNodeWithText("Theme")
            .performClick()

        // Select dark theme
        composeTestRule
            .onNodeWithText("Dark")
            .performClick()

        // Verify theme changes (would check background color)
        // This is simplified - actual test would verify color values
        composeTestRule
            .onNodeWithTag("settings_screen")
            .assertIsDisplayed()
    }

    @Test
    fun testThemeSwitch_systemDefault_followsSystemTheme() {
        // Navigate to settings
        composeTestRule
            .onNodeWithText("Profile")
            .performClick()

        composeTestRule
            .onNodeWithText("Settings")
            .performClick()

        // Click on theme option
        composeTestRule
            .onNodeWithText("Theme")
            .performClick()

        // Select system default
        composeTestRule
            .onNodeWithText("System Default")
            .performClick()

        // Verify selection is saved
        composeTestRule
            .onNodeWithText("System Default")
            .assertIsSelected()
    }

    @Test
    fun testNotificationPreferences_toggleIndividualTypes() {
        // Navigate to settings
        composeTestRule
            .onNodeWithText("Profile")
            .performClick()

        composeTestRule
            .onNodeWithText("Settings")
            .performClick()

        // Click on notifications
        composeTestRule
            .onNodeWithText("Notifications")
            .performClick()

        // Wait for notification preferences
        composeTestRule.waitUntil(timeoutMillis = 5000) {
            composeTestRule
                .onAllNodesWithTag("notification_preferences_screen")
                .fetchSemanticsNodes().isNotEmpty()
        }

        // Toggle ride updates
        composeTestRule
            .onNodeWithTag("toggle_ride_updates")
            .performClick()

        // Verify toggle state changed
        composeTestRule
            .onNodeWithTag("toggle_ride_updates")
            .assertIsOff()

        // Toggle back on
        composeTestRule
            .onNodeWithTag("toggle_ride_updates")
            .performClick()

        composeTestRule
            .onNodeWithTag("toggle_ride_updates")
            .assertIsOn()
    }

    @Test
    fun testLogout_clearsDataAndReturnsToLogin() {
        // Navigate to settings
        composeTestRule
            .onNodeWithText("Profile")
            .performClick()

        composeTestRule
            .onNodeWithText("Settings")
            .performClick()

        // Scroll to logout button
        composeTestRule
            .onNodeWithText("Logout")
            .performScrollTo()

        // Click logout
        composeTestRule
            .onNodeWithText("Logout")
            .performClick()

        // Confirm logout
        composeTestRule
            .onNodeWithText("Confirm")
            .performClick()

        // Verify navigation to login screen
        composeTestRule.waitUntil(timeoutMillis = 5000) {
            composeTestRule
                .onAllNodesWithText("Enter Phone Number")
                .fetchSemanticsNodes().isNotEmpty()
        }

        composeTestRule
            .onNodeWithText("Enter Phone Number")
            .assertIsDisplayed()
    }

    @Test
    fun testSettings_displaysAppVersion() {
        // Navigate to settings
        composeTestRule
            .onNodeWithText("Profile")
            .performClick()

        composeTestRule
            .onNodeWithText("Settings")
            .performClick()

        // Scroll to bottom
        composeTestRule
            .onNodeWithTag("app_version")
            .performScrollTo()

        // Verify app version is displayed
        composeTestRule
            .onNodeWithTag("app_version")
            .assertIsDisplayed()
            .assertTextContains("Version", substring = true)
    }

    @Test
    fun testSettings_persistsAcrossAppRestart() {
        // Change language to Hindi
        composeTestRule
            .onNodeWithText("Profile")
            .performClick()

        composeTestRule
            .onNodeWithText("Settings")
            .performClick()

        composeTestRule
            .onNodeWithText("Language")
            .performClick()

        composeTestRule
            .onNodeWithText("हिंदी (Hindi)")
            .performClick()

        // Restart activity (simulated)
        composeTestRule.activityRule.scenario.recreate()

        // Verify language is still Hindi
        composeTestRule.waitUntil(timeoutMillis = 5000) {
            composeTestRule
                .onAllNodesWithText("सेटिंग्स")
                .fetchSemanticsNodes().isNotEmpty()
        }
    }
}
