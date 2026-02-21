package com.rideconnect.rider.ui.profile

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
 * End-to-end UI tests for profile management features.
 * 
 * Tests cover:
 * - Profile information display and editing
 * - Photo upload
 * - Emergency contacts management
 * - Profile validation
 * 
 * Requirements: 2.1, 2.3, 2.4, 9.7
 */
@HiltAndroidTest
@RunWith(AndroidJUnit4::class)
class ProfileManagementFlowTest {

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
    fun testProfileScreen_displaysUserInformation() {
        // Navigate to profile
        composeTestRule
            .onNodeWithText("Profile")
            .performClick()

        // Wait for profile screen
        composeTestRule.waitUntil(timeoutMillis = 5000) {
            composeTestRule
                .onAllNodesWithTag("profile_screen")
                .fetchSemanticsNodes().isNotEmpty()
        }

        // Verify profile fields are displayed
        composeTestRule
            .onNodeWithTag("name_field")
            .assertIsDisplayed()

        composeTestRule
            .onNodeWithTag("email_field")
            .assertIsDisplayed()

        composeTestRule
            .onNodeWithTag("phone_field")
            .assertIsDisplayed()

        composeTestRule
            .onNodeWithTag("profile_photo")
            .assertIsDisplayed()
    }

    @Test
    fun testProfileUpdate_withValidData_savesSuccessfully() {
        // Navigate to profile
        composeTestRule
            .onNodeWithText("Profile")
            .performClick()

        // Wait for profile screen
        composeTestRule.waitUntil(timeoutMillis = 5000) {
            composeTestRule
                .onAllNodesWithTag("profile_screen")
                .fetchSemanticsNodes().isNotEmpty()
        }

        // Click edit button
        composeTestRule
            .onNodeWithText("Edit")
            .performClick()

        // Update name
        composeTestRule
            .onNodeWithTag("name_field")
            .performTextClearance()

        composeTestRule
            .onNodeWithTag("name_field")
            .performTextInput("John Doe")

        // Update email
        composeTestRule
            .onNodeWithTag("email_field")
            .performTextClearance()

        composeTestRule
            .onNodeWithTag("email_field")
            .performTextInput("john.doe@example.com")

        // Save changes
        composeTestRule
            .onNodeWithText("Save")
            .performClick()

        // Verify success message
        composeTestRule.waitUntil(timeoutMillis = 5000) {
            composeTestRule
                .onAllNodesWithText("Profile updated successfully")
                .fetchSemanticsNodes().isNotEmpty()
        }
    }

    @Test
    fun testProfileUpdate_withInvalidEmail_showsError() {
        // Navigate to profile and edit
        composeTestRule
            .onNodeWithText("Profile")
            .performClick()

        composeTestRule
            .onNodeWithText("Edit")
            .performClick()

        // Enter invalid email
        composeTestRule
            .onNodeWithTag("email_field")
            .performTextClearance()

        composeTestRule
            .onNodeWithTag("email_field")
            .performTextInput("invalid-email")

        // Try to save
        composeTestRule
            .onNodeWithText("Save")
            .performClick()

        // Verify error message
        composeTestRule
            .onNodeWithText("Invalid email format")
            .assertIsDisplayed()
    }

    @Test
    fun testPhotoUpload_selectsAndUploadsImage() {
        // Navigate to profile
        composeTestRule
            .onNodeWithText("Profile")
            .performClick()

        // Click on profile photo
        composeTestRule
            .onNodeWithTag("profile_photo")
            .performClick()

        // Verify photo picker options
        composeTestRule
            .onNodeWithText("Take Photo")
            .assertIsDisplayed()

        composeTestRule
            .onNodeWithText("Choose from Gallery")
            .assertIsDisplayed()

        // Select gallery option (actual image selection would require system interaction)
        composeTestRule
            .onNodeWithText("Choose from Gallery")
            .performClick()

        // After selection, verify upload progress
        composeTestRule.waitUntil(timeoutMillis = 10000) {
            composeTestRule
                .onAllNodesWithText("Uploading...")
                .fetchSemanticsNodes().isNotEmpty()
        }

        // Verify success
        composeTestRule.waitUntil(timeoutMillis = 15000) {
            composeTestRule
                .onAllNodesWithText("Photo updated")
                .fetchSemanticsNodes().isNotEmpty()
        }
    }

    @Test
    fun testEmergencyContacts_addNewContact() {
        // Navigate to profile
        composeTestRule
            .onNodeWithText("Profile")
            .performClick()

        // Navigate to emergency contacts
        composeTestRule
            .onNodeWithText("Emergency Contacts")
            .performClick()

        // Wait for emergency contacts screen
        composeTestRule.waitUntil(timeoutMillis = 5000) {
            composeTestRule
                .onAllNodesWithTag("emergency_contacts_screen")
                .fetchSemanticsNodes().isNotEmpty()
        }

        // Click add contact button
        composeTestRule
            .onNodeWithText("Add Contact")
            .performClick()

        // Enter contact details
        composeTestRule
            .onNodeWithTag("contact_name_input")
            .performTextInput("Jane Doe")

        composeTestRule
            .onNodeWithTag("contact_phone_input")
            .performTextInput("+919876543210")

        // Save contact
        composeTestRule
            .onNodeWithText("Save")
            .performClick()

        // Verify contact is added to list
        composeTestRule.waitUntil(timeoutMillis = 5000) {
            composeTestRule
                .onAllNodesWithText("Jane Doe")
                .fetchSemanticsNodes().isNotEmpty()
        }

        composeTestRule
            .onNodeWithText("Jane Doe")
            .assertIsDisplayed()
    }

    @Test
    fun testEmergencyContacts_removeContact() {
        // Navigate to emergency contacts
        composeTestRule
            .onNodeWithText("Profile")
            .performClick()

        composeTestRule
            .onNodeWithText("Emergency Contacts")
            .performClick()

        // Wait for contacts list
        composeTestRule.waitUntil(timeoutMillis = 5000) {
            composeTestRule
                .onAllNodesWithTag("emergency_contacts_screen")
                .fetchSemanticsNodes().isNotEmpty()
        }

        // Click remove button on first contact
        composeTestRule
            .onNodeWithTag("remove_contact_0")
            .performClick()

        // Confirm removal
        composeTestRule
            .onNodeWithText("Remove")
            .performClick()

        // Verify contact is removed
        composeTestRule.waitUntil(timeoutMillis = 5000) {
            composeTestRule
                .onAllNodesWithTag("contact_item_0")
                .fetchSemanticsNodes().isEmpty()
        }
    }

    @Test
    fun testEmergencyContacts_limitToThree() {
        // Navigate to emergency contacts
        composeTestRule
            .onNodeWithText("Profile")
            .performClick()

        composeTestRule
            .onNodeWithText("Emergency Contacts")
            .performClick()

        // Assume 3 contacts already exist
        // Verify add button is disabled
        composeTestRule
            .onNodeWithText("Add Contact")
            .assertIsNotEnabled()

        // Verify message about limit
        composeTestRule
            .onNodeWithText("Maximum 3 emergency contacts allowed")
            .assertIsDisplayed()
    }
}
