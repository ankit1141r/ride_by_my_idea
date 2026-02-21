# Core UI Module Fix Plan

## Status: In Progress

This document tracks the systematic fixing of 100+ compilation errors in the core:ui module.

## Error Categories

### 1. Missing Imports (HIGH PRIORITY)
- LaunchedEffect - Missing Compose import
- MapType - Missing Google Maps import  
- isGranted, shouldShowRationale - Missing permission API imports
- shouldReduceAnimations - Missing accessibility import

### 2. String Resources (HIGH PRIORITY)
- 30+ unresolved R.string references in ErrorHandler.kt and ErrorComponents.kt
- Solution: Use hardcoded strings or create minimal string resources

### 3. Model Issues (HIGH PRIORITY)
- Place model: latitude/longitude vs location.latitude
- NotificationType, NotificationPreferences - Missing model definitions
- ParcelDelivery.uiState - Missing property

### 4. Function Conflicts (MEDIUM PRIORITY)
- ReceiptRow function defined in both ReceiptScreen.kt and RideReceiptScreen.kt
- Solution: Make one private or rename

### 5. Type Mismatches (MEDIUM PRIORITY)
- MapCameraControl.kt line 131 - Float/Int to String? conversion
- Smart cast issues in multiple screens

### 6. String.format Issues (LOW PRIORITY)
- Multiple files using String.format incorrectly
- Solution: Use Kotlin string templates

### 7. Access Modifiers (LOW PRIORITY)
- CancelRideDialog is private but accessed externally
- adjustCameraBounds function missing

## Fix Strategy

1. Add missing imports
2. Replace R.string references with hardcoded strings (temporary)
3. Fix model property references
4. Resolve function conflicts
5. Fix type mismatches
6. Replace String.format with Kotlin templates
7. Fix access modifiers

## Progress Tracking

- [ ] Phase 1: Missing Imports
- [ ] Phase 2: String Resources
- [ ] Phase 3: Model Issues
- [ ] Phase 4: Function Conflicts
- [ ] Phase 5: Type Mismatches
- [ ] Phase 6: String.format
- [ ] Phase 7: Access Modifiers
