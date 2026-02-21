# Testing Strategy

## Overview

This document outlines the comprehensive testing strategy for the Android Ride-Hailing Application, covering unit tests, integration tests, UI tests, and property-based tests.

## Testing Pyramid

```
        ┌─────────────┐
        │  UI Tests   │  ← Few, slow, expensive
        └─────────────┘
      ┌─────────────────┐
      │ Integration Tests│  ← Some, moderate speed
      └─────────────────┘
    ┌───────────────────────┐
    │     Unit Tests        │  ← Many, fast, cheap
    └───────────────────────┘
```

### Test Distribution

- **Unit Tests**: 70% of tests
- **Integration Tests**: 20% of tests
- **UI Tests**: 10% of tests

## Test Types

### 1. Unit Tests

Test individual components in isolation with mocked dependencies.

**Location:** `src/test/kotlin/`

**What to Test:**
- ViewModel business logic
- Repository implementations
- Data mappers
- Validation logic
- Utility functions

**Example:**
```kotlin
@Test
fun `requestRide should return error when locations are invalid`() = runTest {
    // Given
    val invalidRequest = RideRequest(
        pickupLat = 0.0,
        pickupLng = 0.0,
        dropoffLat = 0.0,
        dropoffLng = 0.0
    )
    
    // When
    val result = viewModel.requestRide(invalidRequest)
    
    // Then
    assertTrue(result is Result.Error)
    assertEquals("Invalid location", (result as Result.Error).message)
}
```

**Tools:**
- JUnit 4
- Mockito Kotlin
- Kotlinx Coroutines Test
- Turbine (for Flow testing)

### 2. Integration Tests

Test interactions between multiple components.

**Location:** `src/test/kotlin/`

**What to Test:**
- Repository + API integration
- Repository + Database integration
- ViewModel + Repository integration
- WebSocket message handling

**Example:**
```kotlin
@Test
fun `repository should cache ride data locally`() = runTest {
    // Given
    val ride = Ride(...)
    coEvery { api.getRide(any()) } returns Response.success(rideDto)
    
    // When
    repository.getRide(rideId).collect()
    
    // Then
    val cachedRide = database.rideDao().getRideById(rideId)
    assertNotNull(cachedRide)
    assertEquals(ride.id, cachedRide.id)
}
```

### 3. UI Tests (Instrumented Tests)

Test user interface and user interactions.

**Location:** `src/androidTest/kotlin/`

**What to Test:**
- Screen rendering
- User interactions (clicks, text input)
- Navigation flows
- State changes reflected in UI

**Example:**
```kotlin
@Test
fun testRideRequestFlow() {
    composeTestRule.setContent {
        RideRequestScreen(...)
    }
    
    // Select pickup location
    composeTestRule
        .onNodeWithTag("pickup_input")
        .performClick()
    
    // Select dropoff location
    composeTestRule
        .onNodeWithTag("dropoff_input")
        .performClick()
    
    // Verify fare estimate shown
    composeTestRule
        .onNodeWithTag("fare_estimate")
        .assertIsDisplayed()
    
    // Request ride
    composeTestRule
        .onNodeWithTag("request_button")
        .performClick()
    
    // Verify tracking screen shown
    composeTestRule
        .onNodeWithTag("tracking_screen")
        .assertIsDisplayed()
}
```

**Tools:**
- Compose Testing
- Espresso
- Hilt Testing
- MockWebServer (for API mocking)

### 4. Property-Based Tests (Optional)

Test universal properties that should hold for all inputs.

**Location:** `src/test/kotlin/`

**What to Test:**
- Input validation properties
- State transition properties
- Data transformation properties

**Example:**
```kotlin
@Test
fun `phone number validation should accept valid formats`() {
    forAll(phoneNumberGenerator) { phoneNumber ->
        val result = PhoneNumberValidator.validate(phoneNumber)
        result.isValid == phoneNumber.matches(validPhoneRegex)
    }
}
```

**Tools:**
- Kotest Property Testing
- Or custom property test framework

## Test Coverage Goals

### Minimum Coverage: 70%

**Coverage by Module:**
- Core Domain: 80%+ (business logic is critical)
- Core Data: 75%+ (data operations are important)
- Core Network: 70%+ (API integration)
- Core Database: 75%+ (data persistence)
- Core Common: 70%+ (shared utilities)
- Rider App: 60%+ (UI-heavy)
- Driver App: 60%+ (UI-heavy)

**Excluded from Coverage:**
- Generated code (Hilt, Room)
- Data classes (DTOs, Entities)
- UI composables (tested via UI tests)
- Android framework classes

## Testing Best Practices

### General Principles

1. **Test Behavior, Not Implementation**: Focus on what the code does, not how
2. **One Assertion Per Test**: Keep tests focused and clear
3. **Arrange-Act-Assert**: Structure tests consistently
4. **Descriptive Names**: Use clear, descriptive test names
5. **Independent Tests**: Tests should not depend on each other
6. **Fast Tests**: Keep unit tests fast (<100ms each)

### Naming Convention

Use descriptive names that explain the test:

```kotlin
// Good
@Test
fun `requestRide should return error when pickup location is invalid`()

// Bad
@Test
fun testRequestRide()
```

### Test Structure

Follow Arrange-Act-Assert pattern:

```kotlin
@Test
fun `test name`() = runTest {
    // Arrange (Given)
    val input = ...
    val expected = ...
    
    // Act (When)
    val result = systemUnderTest.method(input)
    
    // Assert (Then)
    assertEquals(expected, result)
}
```

### Mocking Guidelines

1. **Mock External Dependencies**: API, Database, Device sensors
2. **Don't Mock Domain Models**: Use real instances
3. **Don't Mock Value Objects**: Use real instances
4. **Verify Interactions**: Use `verify` for important calls

```kotlin
@Test
fun `should call API when requesting ride`() = runTest {
    // Given
    val request = RideRequest(...)
    coEvery { api.requestRide(any()) } returns Response.success(rideDto)
    
    // When
    repository.requestRide(request)
    
    // Then
    coVerify { api.requestRide(any()) }
}
```

### Testing Coroutines

Use `runTest` for coroutine tests:

```kotlin
@Test
fun `test coroutine function`() = runTest {
    // Test code with coroutines
    val result = suspendFunction()
    assertEquals(expected, result)
}
```

### Testing Flows

Use Turbine for Flow testing:

```kotlin
@Test
fun `should emit loading then success`() = runTest {
    repository.getData().test {
        // First emission
        assertEquals(Result.Loading, awaitItem())
        
        // Second emission
        val result = awaitItem()
        assertTrue(result is Result.Success)
        
        awaitComplete()
    }
}
```

### Testing ViewModels

Test ViewModel state changes:

```kotlin
@Test
fun `login should update state to success`() = runTest {
    // Given
    val phone = "1234567890"
    coEvery { repository.sendOtp(phone) } returns Result.Success(Unit)
    
    // When
    viewModel.sendOtp(phone)
    
    // Then
    val state = viewModel.state.value
    assertTrue(state is LoginState.OtpSent)
}
```

### Testing Compose UI

Use semantic properties for testing:

```kotlin
@Composable
fun MyButton(onClick: () -> Unit) {
    Button(
        onClick = onClick,
        modifier = Modifier.testTag("my_button")  // Add test tag
    ) {
        Text("Click Me")
    }
}

@Test
fun testButton() {
    composeTestRule.setContent {
        MyButton(onClick = {})
    }
    
    composeTestRule
        .onNodeWithTag("my_button")
        .assertIsDisplayed()
        .performClick()
}
```

## Running Tests

### Command Line

**All Unit Tests:**
```bash
./gradlew test
```

**Specific Module:**
```bash
./gradlew :core:domain:testDebugUnitTest
```

**All UI Tests:**
```bash
./gradlew connectedAndroidTest
```

**Specific App:**
```bash
./gradlew :rider-app:connectedDevDebugAndroidTest
```

**With Coverage:**
```bash
./gradlew testDebugUnitTest jacocoTestReport
```

### Android Studio

1. Right-click on test file/class/method
2. Select "Run 'TestName'"
3. View results in Run window

### Continuous Integration

Tests run automatically on:
- Every commit to feature branches
- Pull requests
- Merge to main branch

**CI Configuration:**
```yaml
- name: Run Unit Tests
  run: ./gradlew test

- name: Run UI Tests
  run: ./gradlew connectedAndroidTest

- name: Generate Coverage Report
  run: ./gradlew jacocoTestReport

- name: Verify Coverage Threshold
  run: ./gradlew jacocoTestCoverageVerification
```

## Test Data Management

### Test Fixtures

Create reusable test data:

```kotlin
object TestFixtures {
    fun createRide(
        id: String = "ride123",
        status: RideStatus = RideStatus.REQUESTED,
        fare: Double = 10.0
    ) = Ride(
        id = id,
        status = status,
        fare = fare,
        // ... other fields
    )
}
```

### Mock Responses

Use MockWebServer for API testing:

```kotlin
@Before
fun setup() {
    mockWebServer = MockWebServer()
    mockWebServer.start()
    
    // Configure Retrofit to use mock server
    retrofit = Retrofit.Builder()
        .baseUrl(mockWebServer.url("/"))
        .build()
}

@Test
fun `test API call`() = runTest {
    // Enqueue mock response
    mockWebServer.enqueue(
        MockResponse()
            .setResponseCode(200)
            .setBody("""{"id": "ride123"}""")
    )
    
    // Make API call
    val response = api.getRide("ride123")
    
    // Verify
    assertTrue(response.isSuccessful)
}
```

## Debugging Tests

### Failed Test Investigation

1. **Read Error Message**: Understand what failed
2. **Check Test Logs**: Review Logcat output
3. **Add Debug Logging**: Add temporary logs
4. **Run in Debug Mode**: Set breakpoints
5. **Isolate Issue**: Run single test

### Common Issues

**Flaky Tests:**
- Use `runTest` for coroutine tests
- Avoid hardcoded delays
- Use `awaitItem()` for Flow testing
- Ensure test independence

**Slow Tests:**
- Mock expensive operations
- Use in-memory database
- Avoid Thread.sleep()
- Run tests in parallel

**Test Pollution:**
- Clean up after each test
- Use `@Before` and `@After`
- Don't share mutable state

## Test Maintenance

### When to Update Tests

- When requirements change
- When bugs are found (add regression test)
- When refactoring code
- When test becomes flaky

### Test Refactoring

- Extract common setup to `@Before`
- Create test utilities for repeated logic
- Use test fixtures for test data
- Keep tests DRY (Don't Repeat Yourself)

### Removing Tests

Only remove tests when:
- Feature is completely removed
- Test is redundant (covered by other tests)
- Test is no longer valid

## Metrics and Reporting

### Coverage Reports

View coverage report after running:
```bash
./gradlew jacocoTestReport
```

Report location: `build/reports/jacoco/jacocoTestReport/html/index.html`

### Test Reports

View test results:
- Unit tests: `build/reports/tests/testDebugUnitTest/index.html`
- UI tests: `build/reports/androidTests/connected/index.html`

### CI Metrics

Track over time:
- Test pass rate
- Code coverage percentage
- Test execution time
- Flaky test rate

## Resources

- [Android Testing Documentation](https://developer.android.com/training/testing)
- [Compose Testing Documentation](https://developer.android.com/jetpack/compose/testing)
- [Kotlin Coroutines Testing](https://kotlinlang.org/docs/coroutines-testing.html)
- [Mockito Documentation](https://site.mockito.org/)
- [JUnit 4 Documentation](https://junit.org/junit4/)
