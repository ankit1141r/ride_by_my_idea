# Accessibility Testing Checklist

## Overview

This document provides a comprehensive testing checklist for verifying WCAG 2.1 Level AA compliance and assistive technology support in the RideConnect Android applications.

## Testing Tools Required

1. **Android Accessibility Scanner** - Install from Play Store
2. **TalkBack Screen Reader** - Built into Android
3. **External Bluetooth Keyboard** - For keyboard navigation testing
4. **Contrast Checker Tool** - WebAIM Contrast Checker or similar
5. **Physical Android Device** - For accurate testing (emulator limitations)

## Test Environment Setup

### Enable Developer Options
1. Go to Settings → About Phone
2. Tap "Build Number" 7 times
3. Go to Settings → System → Developer Options
4. Enable "Show layout bounds" for touch target verification

### Enable TalkBack
1. Go to Settings → Accessibility → TalkBack
2. Toggle TalkBack ON
3. Complete the tutorial

### Configure Large Text
1. Go to Settings → Display → Font size → Largest
2. Go to Settings → Display → Display size → Largest

## Task 31.1: Content Descriptions Testing

### Test Procedure
1. Enable TalkBack
2. Navigate through each screen using swipe gestures
3. Verify each interactive element announces its purpose clearly

### Screens to Test

#### Login Screen
- [ ] Phone number input field announces "Enter your phone number"
- [ ] Send OTP button announces "Send verification code"
- [ ] OTP digit inputs announce "Enter digit 1 of 6", "Enter digit 2 of 6", etc.
- [ ] Verify button announces "Verify code and log in"
- [ ] Biometric login button announces "Log in with fingerprint" or "Log in with face recognition"

#### Home Screen (Rider)
- [ ] Pickup location field announces "Select pickup location"
- [ ] Dropoff location field announces "Select dropoff location"
- [ ] Request ride button announces "Request ride for estimated fare [amount]"
- [ ] Menu button announces "Open navigation menu"
- [ ] Profile icon announces "View profile"

#### Home Screen (Driver)
- [ ] Online/Offline toggle announces current state and action
- [ ] Earnings display announces "Today's earnings: [amount]"
- [ ] Menu button announces "Open navigation drawer"

#### Active Ride Screen
- [ ] Driver/Rider location marker announces distance and ETA
- [ ] Call button announces "Call driver" or "Call rider"
- [ ] Chat button announces "Open chat with driver" or "Open chat with rider"
- [ ] SOS button announces "Emergency SOS - Send alert to contacts"
- [ ] Start/Complete ride buttons announce their action

#### Payment Screen
- [ ] Payment method selector announces selected method
- [ ] Fare breakdown items announce amount and description
- [ ] Confirm payment button announces "Confirm payment of [amount]"
- [ ] Receipt button announces "View receipt"

#### Rating Screen
- [ ] Star rating announces "Rate driver [X] out of 5 stars"
- [ ] Review input announces "Write optional review"
- [ ] Submit button announces "Submit rating"

#### Settings Screen
- [ ] Each setting announces its current value
- [ ] Toggle switches announce on/off state
- [ ] Language selector announces current language
- [ ] Theme selector announces current theme
- [ ] Logout button announces "Log out of account"

### Pass Criteria
- ✅ All interactive elements have meaningful content descriptions
- ✅ Content descriptions are concise and clear
- ✅ Button states (enabled/disabled) are announced
- ✅ Current values are announced for inputs and selectors
- ✅ Error messages are announced when they appear
- ✅ Loading states are announced

## Task 31.2: Minimum Touch Target Size Testing

### Test Procedure
1. Enable "Show layout bounds" in Developer Options
2. Navigate through each screen
3. Measure interactive elements (should be at least 48dp × 48dp)
4. Test tapping on small devices

### Elements to Verify

#### All Screens
- [ ] All buttons are at least 48dp × 48dp
- [ ] All icon buttons are at least 48dp × 48dp
- [ ] All clickable cards/items are at least 48dp tall
- [ ] All toggle switches are at least 48dp × 48dp
- [ ] All radio buttons/checkboxes are at least 48dp × 48dp
- [ ] Adequate spacing between adjacent touch targets (at least 8dp)

#### Specific Components
- [ ] Navigation bar icons: 48dp × 48dp
- [ ] Floating action buttons: 56dp × 56dp (standard FAB size)
- [ ] List item touch targets: Full width, at least 48dp height
- [ ] Map markers: At least 48dp × 48dp touch area
- [ ] Star rating buttons: At least 48dp × 48dp each

### Pass Criteria
- ✅ All interactive elements meet minimum 48dp × 48dp size
- ✅ No overlapping touch targets
- ✅ Comfortable tapping on small devices (5-inch screens)
- ✅ No accidental taps on adjacent elements

## Task 31.4: Color Contrast Ratio Testing

### Test Procedure
1. Use Android Accessibility Scanner
2. Use WebAIM Contrast Checker for specific elements
3. Test both light and dark themes
4. Verify all text and UI components

### Contrast Requirements
- Normal text (< 18pt): 4.5:1 minimum
- Large text (≥ 18pt): 3:1 minimum
- UI components: 3:1 minimum

### Elements to Test

#### Light Theme
- [ ] Primary text on background: ≥ 4.5:1
- [ ] Secondary text on background: ≥ 4.5:1
- [ ] Button text on button background: ≥ 4.5:1
- [ ] Error text on background: ≥ 4.5:1
- [ ] Link text on background: ≥ 4.5:1
- [ ] Icon colors on background: ≥ 3:1
- [ ] Border colors: ≥ 3:1
- [ ] Focus indicators: ≥ 3:1

#### Dark Theme
- [ ] Primary text on background: ≥ 4.5:1
- [ ] Secondary text on background: ≥ 4.5:1
- [ ] Button text on button background: ≥ 4.5:1
- [ ] Error text on background: ≥ 4.5:1
- [ ] Link text on background: ≥ 4.5:1
- [ ] Icon colors on background: ≥ 3:1
- [ ] Border colors: ≥ 3:1
- [ ] Focus indicators: ≥ 3:1

#### Map Elements
- [ ] Map markers in light mode: ≥ 3:1
- [ ] Map markers in dark mode: ≥ 3:1
- [ ] Route polylines in light mode: ≥ 3:1
- [ ] Route polylines in dark mode: ≥ 3:1

### Pass Criteria
- ✅ All text meets 4.5:1 contrast ratio (normal text)
- ✅ Large text meets 3:1 contrast ratio
- ✅ UI components meet 3:1 contrast ratio
- ✅ Both light and dark themes comply
- ✅ No accessibility scanner warnings for contrast

## Task 31.6: Text Scaling Support Testing

### Test Procedure
1. Set font size to Largest
2. Set display size to Largest
3. Navigate through all screens
4. Verify no text truncation or layout breaks

### Screens to Test

#### All Screens
- [ ] Text scales up to 200% without truncation
- [ ] Layouts don't break with large text
- [ ] All content remains accessible
- [ ] Scrolling works properly
- [ ] Buttons expand to accommodate text
- [ ] No overlapping text
- [ ] Multi-line text wraps correctly

#### Specific Scenarios
- [ ] Long ride addresses display fully
- [ ] Fare breakdowns remain readable
- [ ] Chat messages wrap correctly
- [ ] Error messages display fully
- [ ] Button labels don't overflow
- [ ] Navigation labels remain visible
- [ ] Settings options display fully

### Pass Criteria
- ✅ All text scales up to 200% without issues
- ✅ No text truncation with ellipsis (...)
- ✅ Layouts adapt to larger text
- ✅ All content remains accessible
- ✅ Scrolling works for overflowing content

## Task 31.7: Haptic Feedback Testing

### Test Procedure
1. Enable vibration in device settings
2. Test each action that should provide feedback
3. Verify appropriate vibration strength

### Actions to Test

#### Standard Haptic Feedback (50ms vibration)
- [ ] Ride request confirmation
- [ ] Driver accepting ride
- [ ] Driver rejecting ride
- [ ] Payment confirmation
- [ ] Rating submission
- [ ] Emergency contact call button
- [ ] Settings toggle switches
- [ ] Navigation button taps

#### Strong Haptic Feedback (Pattern vibration)
- [ ] SOS button activation
- [ ] Emergency alert received
- [ ] Critical error occurred

#### Notification Vibrations
- [ ] Ride accepted notification
- [ ] Driver arriving notification
- [ ] Ride started notification
- [ ] Ride completed notification
- [ ] New message notification
- [ ] Payment success notification

### Pass Criteria
- ✅ Standard actions provide brief vibration
- ✅ Critical actions provide strong vibration pattern
- ✅ Vibration strength appropriate for action importance
- ✅ Notifications vibrate when app in background
- ✅ Haptic feedback respects device settings

## Task 31.8: Keyboard and Switch Navigation Testing

### Keyboard Navigation Test Procedure
1. Connect Bluetooth keyboard to device
2. Navigate through app using keyboard
3. Verify all features are accessible

### Keyboard Navigation Tests

#### Basic Navigation
- [ ] Tab key moves focus to next element
- [ ] Shift+Tab moves focus to previous element
- [ ] Enter/Space activates focused button
- [ ] Arrow keys navigate lists
- [ ] Escape dismisses dialogs
- [ ] Focus indicators are visible

#### Screen-Specific Tests
- [ ] Login: Tab through phone input → Send OTP → OTP inputs → Verify
- [ ] Home: Tab through location fields → Request ride button
- [ ] Active Ride: Tab through Call → Chat → SOS buttons
- [ ] Payment: Tab through payment methods → Confirm button
- [ ] Settings: Tab through all settings options

### Switch Access Test Procedure
1. Enable Switch Access: Settings → Accessibility → Switch Access
2. Configure switches (e.g., volume buttons)
3. Navigate through app using switches

### Switch Access Tests
- [ ] All interactive elements are reachable
- [ ] Actions can be performed via switches
- [ ] Navigation is efficient (not too many steps)
- [ ] Focus indicators are clear
- [ ] Dialogs can be dismissed
- [ ] Lists can be scrolled

### Pass Criteria
- ✅ All features accessible via keyboard
- ✅ Logical focus order
- ✅ Visible focus indicators
- ✅ All actions can be performed
- ✅ Switch Access works for all features

## Android Accessibility Scanner Testing

### Test Procedure
1. Install Accessibility Scanner from Play Store
2. Enable scanner in Accessibility settings
3. Navigate to each screen
4. Tap scanner floating button
5. Review and document issues

### Screens to Scan
- [ ] Login Screen
- [ ] Home Screen (Rider)
- [ ] Home Screen (Driver)
- [ ] Ride Request Screen
- [ ] Active Ride Screen
- [ ] Payment Screen
- [ ] Rating Screen
- [ ] Chat Screen
- [ ] Profile Screen
- [ ] Settings Screen
- [ ] Emergency Contacts Screen
- [ ] Ride History Screen

### Issues to Check
- [ ] Content descriptions missing
- [ ] Touch targets too small
- [ ] Low contrast text
- [ ] Clickable items not labeled
- [ ] Text too small
- [ ] Item descriptions unclear

### Pass Criteria
- ✅ No critical issues reported
- ✅ All suggestions addressed or documented
- ✅ Scanner gives green checkmark for all screens

## Regression Testing

### After Each Code Change
- [ ] Run Accessibility Scanner on modified screens
- [ ] Test with TalkBack on modified screens
- [ ] Verify touch target sizes maintained
- [ ] Check contrast ratios not affected

### Before Each Release
- [ ] Complete full accessibility test suite
- [ ] Test on multiple devices (small, medium, large screens)
- [ ] Test on different Android versions (8.0 to 14)
- [ ] Document any known issues

## Test Results Documentation

### Test Report Template

```
Date: [Date]
Tester: [Name]
Device: [Device Model]
Android Version: [Version]
App Version: [Version]

Task 31.1 - Content Descriptions: [PASS/FAIL]
Issues: [List any issues]

Task 31.2 - Touch Target Sizes: [PASS/FAIL]
Issues: [List any issues]

Task 31.4 - Color Contrast: [PASS/FAIL]
Issues: [List any issues]

Task 31.6 - Text Scaling: [PASS/FAIL]
Issues: [List any issues]

Task 31.7 - Haptic Feedback: [PASS/FAIL]
Issues: [List any issues]

Task 31.8 - Keyboard Navigation: [PASS/FAIL]
Issues: [List any issues]

Overall Result: [PASS/FAIL]
```

## Known Limitations

- Emulators may not accurately test haptic feedback
- TalkBack behavior may vary between Android versions
- Some third-party libraries may have accessibility limitations
- Map components have inherent accessibility challenges

## Resources

- [Android Accessibility Testing Guide](https://developer.android.com/guide/topics/ui/accessibility/testing)
- [WCAG 2.1 Quick Reference](https://www.w3.org/WAI/WCAG21/quickref/)
- [Material Design Accessibility](https://m3.material.io/foundations/accessible-design/overview)
- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
