# Accessibility Implementation Guide

## Overview

This guide documents the accessibility features implemented in the RideConnect Android applications to ensure WCAG 2.1 Level AA compliance and support for assistive technologies.

## Implemented Features

### 1. Content Descriptions (Requirement 25.1, 25.2)

All interactive UI elements have content descriptions for TalkBack screen reader support.

**Implementation:**
- Use `Modifier.accessibleDescription()` for non-interactive elements
- Use `Modifier.accessibleClickable()` for interactive elements
- Content descriptions are clear, concise, and describe the element's purpose

**Testing with TalkBack:**
1. Enable TalkBack: Settings → Accessibility → TalkBack → On
2. Navigate through the app using swipe gestures
3. Verify all interactive elements announce their purpose
4. Verify button states (enabled/disabled) are announced

### 2. Minimum Touch Target Sizes (Requirement 25.3)

All interactive elements meet the minimum 48dp × 48dp touch target size.

**Implementation:**
- Use `Modifier.accessibleTouchTarget()` for all clickable elements
- Automatically applies `defaultMinSize(48.dp, 48.dp)`
- Ensures comfortable tapping for users with motor impairments

**Testing:**
- Enable "Show layout bounds" in Developer Options
- Verify all buttons, icons, and clickable elements are at least 48dp × 48dp
- Test on physical devices with different screen sizes

### 3. Color Contrast Ratios (Requirement 25.4)

All text and interactive elements meet WCAG 2.1 Level AA contrast requirements:
- Normal text (< 18pt): 4.5:1 contrast ratio
- Large text (≥ 18pt): 3:1 contrast ratio
- UI components: 3:1 contrast ratio

**Implementation:**
- Material Design 3 color schemes ensure proper contrast
- Both light and dark themes tested for compliance
- Map markers and polylines adjusted for dark mode visibility

**Testing Tools:**
- Use Android Accessibility Scanner app
- Use online contrast checkers (e.g., WebAIM Contrast Checker)
- Test with "Remove animations" and "High contrast text" enabled

### 4. Text Scaling Support (Requirement 25.5)

Layouts support text scaling up to 200% without breaking or truncating content.

**Implementation:**
- Use `sp` units for all text sizes
- Avoid fixed height containers for text
- Use `Column` with `verticalScroll` for scrollable content
- Test with different font scale settings

**Testing:**
1. Go to Settings → Display → Font size → Largest
2. Go to Settings → Display → Display size → Largest
3. Navigate through all screens
4. Verify no text is cut off or overlapping
5. Verify all content remains accessible

### 5. Haptic Feedback (Requirement 25.6)

Haptic feedback provided for important actions and notifications.

**Implementation:**
- `AccessibilityUtils.provideHapticFeedback()` for standard actions
- `AccessibilityUtils.provideStrongHapticFeedback()` for critical actions (SOS)
- Integrated with `Modifier.accessibleClickable(provideHapticFeedback = true)`

**Haptic Feedback Locations:**
- Ride request confirmation
- Driver accepting/rejecting rides
- Payment confirmation
- Rating submission
- SOS button activation (strong feedback)
- Emergency contact calls
- Ride status changes (via notifications)

**Testing:**
- Enable vibration in device settings
- Test each action that should provide feedback
- Verify appropriate vibration strength for action importance

### 6. Keyboard and Switch Navigation (Requirement 25.7)

All features accessible via external keyboard and switch controls.

**Implementation:**
- Proper focus order for all interactive elements
- Tab navigation support
- Enter/Space key activation for buttons
- Arrow key navigation for lists
- Escape key for dismissing dialogs

**Testing with External Keyboard:**
1. Connect Bluetooth keyboard to device
2. Use Tab key to navigate between elements
3. Use Enter/Space to activate buttons
4. Use Arrow keys to navigate lists
5. Use Escape to dismiss dialogs
6. Verify focus indicators are visible

**Testing with Switch Access:**
1. Enable Switch Access: Settings → Accessibility → Switch Access
2. Configure switches (e.g., volume buttons)
3. Navigate through app using switches
4. Verify all interactive elements are reachable
5. Verify actions can be performed

## Accessibility Utilities

### AccessibilityUtils Object

Located in `core/common/src/main/kotlin/com/rideconnect/core/common/accessibility/AccessibilityUtils.kt`

**Methods:**
- `provideHapticFeedback(context, duration)` - Standard haptic feedback
- `provideStrongHapticFeedback(context)` - Strong haptic feedback for critical actions

**Constants:**
- `MIN_TOUCH_TARGET_SIZE` - 48.dp minimum touch target

### Modifier Extensions

**`Modifier.accessibleTouchTarget()`**
- Ensures minimum 48dp × 48dp touch target size
- Use for all interactive elements

**`Modifier.accessibleDescription(description: String)`**
- Adds content description for screen readers
- Use for non-interactive informational elements

**`Modifier.accessibleClickable(contentDescription, enabled, provideHapticFeedback, onClick)`**
- Combines touch target, content description, and haptic feedback
- Use for all clickable elements
- Automatically handles ripple effect and interaction source

## Usage Examples

### Button with Accessibility Support

```kotlin
Button(
    onClick = { /* action */ },
    modifier = Modifier.accessibleClickable(
        contentDescription = "Request ride",
        provideHapticFeedback = true,
        onClick = { /* action */ }
    )
) {
    Text("Request Ride")
}
```

### Icon Button with Content Description

```kotlin
IconButton(
    onClick = { /* action */ },
    modifier = Modifier
        .accessibleTouchTarget()
        .accessibleDescription("Open settings")
) {
    Icon(Icons.Default.Settings, contentDescription = null)
}
```

### Critical Action with Strong Haptic Feedback

```kotlin
val context = LocalContext.current

Button(
    onClick = {
        AccessibilityUtils.provideStrongHapticFeedback(context)
        triggerSOS()
    },
    modifier = Modifier.accessibleTouchTarget(),
    colors = ButtonDefaults.buttonColors(containerColor = Color.Red)
) {
    Text("SOS Emergency")
}
```

## Screen-Specific Accessibility Features

### Login Screen
- Phone number input: "Enter your phone number"
- Send OTP button: "Send verification code"
- OTP input fields: "Enter digit 1 of 6", "Enter digit 2 of 6", etc.
- Verify button: "Verify code and log in"

### Ride Request Screen
- Pickup location: "Select pickup location"
- Dropoff location: "Select dropoff location"
- Request ride button: "Request ride for estimated fare [amount]"
- Cancel button: "Cancel ride request"

### Active Ride Screen
- Driver location marker: "Driver is [distance] away"
- ETA display: "Estimated arrival in [time]"
- Call driver button: "Call driver"
- Chat button: "Open chat with driver"
- SOS button: "Emergency SOS - Send alert to contacts"

### Payment Screen
- Payment method selector: "Select payment method"
- Confirm payment button: "Confirm payment of [amount]"
- Receipt button: "View receipt"

### Rating Screen
- Star rating: "Rate driver [X] out of 5 stars"
- Review input: "Write optional review"
- Submit button: "Submit rating"

## Testing Checklist

### TalkBack Testing
- [ ] All buttons announce their purpose
- [ ] All input fields announce their label and current value
- [ ] All images have meaningful descriptions
- [ ] Navigation between elements is logical
- [ ] Button states (enabled/disabled) are announced
- [ ] Error messages are announced
- [ ] Loading states are announced

### Touch Target Testing
- [ ] All interactive elements are at least 48dp × 48dp
- [ ] Adequate spacing between adjacent touch targets
- [ ] Touch targets don't overlap

### Color Contrast Testing
- [ ] All text meets 4.5:1 contrast ratio (normal text)
- [ ] Large text meets 3:1 contrast ratio
- [ ] UI components meet 3:1 contrast ratio
- [ ] Both light and dark themes comply

### Text Scaling Testing
- [ ] Text scales up to 200% without truncation
- [ ] Layouts don't break with large text
- [ ] All content remains accessible
- [ ] Scrolling works properly with scaled text

### Haptic Feedback Testing
- [ ] Standard actions provide brief vibration
- [ ] Critical actions provide strong vibration pattern
- [ ] Feedback is appropriate for action importance

### Keyboard Navigation Testing
- [ ] Tab key navigates between elements
- [ ] Focus order is logical
- [ ] Enter/Space activates buttons
- [ ] Arrow keys navigate lists
- [ ] Escape dismisses dialogs
- [ ] Focus indicators are visible

### Switch Access Testing
- [ ] All interactive elements are reachable
- [ ] Actions can be performed via switches
- [ ] Navigation is efficient

## Accessibility Scanner Results

Run the Android Accessibility Scanner app on all screens to identify issues:

1. Install Accessibility Scanner from Play Store
2. Enable the scanner in Accessibility settings
3. Navigate to each screen in the app
4. Tap the scanner floating button
5. Review and fix any reported issues

## Continuous Accessibility Testing

### Automated Tests
- Use Espresso with accessibility checks enabled
- Run tests with TalkBack enabled
- Verify content descriptions in UI tests

### Manual Testing Schedule
- Test with TalkBack before each release
- Test with large text sizes weekly
- Test with external keyboard monthly
- Test with Switch Access quarterly

## Resources

- [Android Accessibility Guide](https://developer.android.com/guide/topics/ui/accessibility)
- [Material Design Accessibility](https://m3.material.io/foundations/accessible-design/overview)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [WebAIM Contrast Checker](https://webaim.org/resources/contrastchecker/)
- [Android Accessibility Scanner](https://play.google.com/store/apps/details?id=com.google.android.apps.accessibility.auditor)

## Notes

- Accessibility is not a one-time implementation but an ongoing commitment
- Test with real users who rely on assistive technologies when possible
- Prioritize accessibility from the design phase, not as an afterthought
- Keep content descriptions updated when UI changes
- Consider accessibility in all new feature development
