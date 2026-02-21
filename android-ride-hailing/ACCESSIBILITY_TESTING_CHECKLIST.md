# Accessibility Testing Checklist

## Overview

This checklist guides you through accessibility testing for the Android Ride-Hailing Application to ensure WCAG 2.1 Level AA compliance and usability for all users.

---

## 1. Screen Reader Testing (TalkBack)

### TalkBack Setup

**Steps:**
1. Enable TalkBack:
   - Settings → Accessibility → TalkBack → Turn On
2. Learn TalkBack gestures:
   - Swipe right: Next item
   - Swipe left: Previous item
   - Double tap: Activate
   - Two-finger swipe: Scroll

### Content Description Test

**Test all screens for proper content descriptions:**

**Rider App Screens:**
- [ ] Login Screen
  - Phone input has description
  - Send OTP button has description
  - All icons have descriptions
- [ ] Home Screen
  - Map has description
  - Location search has description
  - Ride request button has description
  - All navigation items have descriptions
- [ ] Ride Request Screen
  - Pickup location has description
  - Dropoff location has description
  - Vehicle type buttons have descriptions
  - Fare estimate has description
- [ ] Active Ride Screen
  - Driver info has descriptions
  - Map has description
  - ETA has description
  - Action buttons have descriptions
- [ ] Profile Screen
  - Photo has description
  - Edit fields have descriptions
  - Save button has description
- [ ] Settings Screen
  - All toggles have descriptions
  - All options have descriptions

**Driver App Screens:**
- [ ] Driver Home Screen
  - Online/offline toggle has description
  - Earnings summary has description
  - Map has description
- [ ] Ride Request Dialog
  - Pickup/dropoff have descriptions
  - Accept/reject buttons have descriptions
  - Timer has description
- [ ] Active Ride Screen
  - Navigation has description
  - Rider info has description
  - Action buttons have descriptions
- [ ] Earnings Screen
  - All statistics have descriptions
  - Ride list items have descriptions

**Test Results:**
- [ ] All interactive elements have content descriptions
- [ ] Descriptions are clear and meaningful
- [ ] Decorative images marked as decorative
- [ ] Document missing descriptions: _____________________

### Navigation Test

**Steps:**
1. Enable TalkBack
2. Navigate through each screen using swipe gestures
3. Verify logical reading order
4. Test all interactive elements

**Expected Results:**
- Reading order is logical (top to bottom, left to right)
- All interactive elements are reachable
- Focus moves correctly between elements
- No focus traps

**Test Results:**
- [ ] Reading order is logical
- [ ] All elements reachable
- [ ] Focus navigation works
- [ ] No focus traps found
- [ ] Document any issues: _____________________

### Announcement Test

**Steps:**
1. Enable TalkBack
2. Perform actions that trigger state changes:
   - Submit form
   - Show error message
   - Load data
   - Update status
3. Verify announcements

**Expected Results:**
- State changes announced
- Error messages announced
- Loading states announced
- Success messages announced

**Test Results:**
- [ ] State changes announced
- [ ] Errors announced
- [ ] Loading announced
- [ ] Success announced
- [ ] Document any issues: _____________________

### Button and Link Test

**Steps:**
1. Enable TalkBack
2. Navigate to all buttons and links
3. Verify they're announced correctly

**Expected Results:**
- Buttons announced as "Button"
- Links announced as "Link"
- Purpose is clear from label

**Test Results:**
- [ ] Buttons announced correctly
- [ ] Links announced correctly
- [ ] Labels are clear
- [ ] Document any issues: _____________________

---

## 2. Touch Target Size Testing

### Minimum Size Verification

**Requirement:** All interactive elements must be at least 48dp × 48dp

**Test Method:**
1. Enable "Show layout bounds" in Developer Options
2. Visually inspect all interactive elements
3. Measure small elements

**Elements to Test:**

**Rider App:**
- [ ] Login button: _____ dp × _____ dp
- [ ] OTP input fields: _____ dp × _____ dp
- [ ] Location search icon: _____ dp × _____ dp
- [ ] Vehicle type buttons: _____ dp × _____ dp
- [ ] Ride request button: _____ dp × _____ dp
- [ ] Cancel ride button: _____ dp × _____ dp
- [ ] Chat button: _____ dp × _____ dp
- [ ] SOS button: _____ dp × _____ dp
- [ ] Rating stars: _____ dp × _____ dp
- [ ] Navigation icons: _____ dp × _____ dp
- [ ] Settings toggles: _____ dp × _____ dp

**Driver App:**
- [ ] Online/offline toggle: _____ dp × _____ dp
- [ ] Accept ride button: _____ dp × _____ dp
- [ ] Reject ride button: _____ dp × _____ dp
- [ ] Start ride button: _____ dp × _____ dp
- [ ] Complete ride button: _____ dp × _____ dp
- [ ] Navigation drawer icon: _____ dp × _____ dp
- [ ] Earnings filter buttons: _____ dp × _____ dp

**Test Results:**
- [ ] All elements meet 48dp minimum
- [ ] Document undersized elements: _____________________

### Touch Target Spacing Test

**Steps:**
1. Check spacing between adjacent interactive elements
2. Verify at least 8dp spacing

**Test Results:**
- [ ] Adequate spacing between elements
- [ ] No accidental taps
- [ ] Document any issues: _____________________

---

## 3. Color Contrast Testing

### Text Contrast Test

**Requirement:** 
- Normal text (< 18pt): 4.5:1 contrast ratio
- Large text (≥ 18pt): 3:1 contrast ratio

**Test Method:**
1. Use Accessibility Scanner app
2. Or use online contrast checker with screenshots
3. Test in both light and dark modes

**Elements to Test:**

**Light Mode:**
- [ ] Body text: _____ : 1 (Target: ≥ 4.5:1)
- [ ] Button text: _____ : 1 (Target: ≥ 4.5:1)
- [ ] Link text: _____ : 1 (Target: ≥ 4.5:1)
- [ ] Error text: _____ : 1 (Target: ≥ 4.5:1)
- [ ] Placeholder text: _____ : 1 (Target: ≥ 4.5:1)
- [ ] Disabled text: _____ : 1 (Target: ≥ 3:1)
- [ ] Large headings: _____ : 1 (Target: ≥ 3:1)

**Dark Mode:**
- [ ] Body text: _____ : 1 (Target: ≥ 4.5:1)
- [ ] Button text: _____ : 1 (Target: ≥ 4.5:1)
- [ ] Link text: _____ : 1 (Target: ≥ 4.5:1)
- [ ] Error text: _____ : 1 (Target: ≥ 4.5:1)
- [ ] Placeholder text: _____ : 1 (Target: ≥ 4.5:1)
- [ ] Disabled text: _____ : 1 (Target: ≥ 3:1)
- [ ] Large headings: _____ : 1 (