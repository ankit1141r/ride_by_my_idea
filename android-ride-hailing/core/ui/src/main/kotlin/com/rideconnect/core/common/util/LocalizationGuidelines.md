# Localization Guidelines

## Dynamic Content Preservation (Requirement 21.7)

### What NOT to Translate

The following types of content should NEVER be translated and must be displayed in their original language:

1. **User Names**: Display names exactly as entered by users
2. **Addresses**: Street names, city names, and location descriptions from Google Places API
3. **User-Generated Content**: 
   - Chat messages
   - Reviews and ratings text
   - Delivery instructions
   - Cancellation reasons
4. **Place Names**: Restaurant names, landmark names, etc.
5. **Vehicle Details**: License plate numbers, vehicle make/model names

### What TO Translate

Only translate static UI elements defined in `strings.xml`:
- Button labels
- Screen titles
- Error messages
- System notifications
- Form field labels
- Menu items

### Implementation

All dynamic content from the API is displayed as-is without any translation processing:

```kotlin
// CORRECT - Display user name as-is
Text(text = user.name)

// CORRECT - Display address as-is
Text(text = ride.pickupLocation.address)

// CORRECT - Display chat message as-is
Text(text = chatMessage.message)

// CORRECT - Use string resource for UI labels
Text(text = stringResource(R.string.pickup_location))
```

### Testing

When testing localization:
1. Switch app language to Hindi
2. Verify all UI labels are translated
3. Verify user names, addresses, and messages remain in original language
4. Test with mixed English/Hindi content to ensure proper display
