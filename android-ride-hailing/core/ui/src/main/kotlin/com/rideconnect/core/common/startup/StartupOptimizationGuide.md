# App Startup Optimization Guide

## Overview

This guide explains the startup optimization strategies implemented to meet the 2-second startup time requirement (Requirement 23.1).

## Optimization Strategies

### 1. Lazy Initialization

Non-critical components are initialized asynchronously after the main UI is displayed:

- **Critical Components** (initialized synchronously):
  - Dependency injection (Hilt)
  - Authentication state
  - Language preferences
  - Theme configuration

- **Non-Critical Components** (initialized asynchronously):
  - Analytics and crash reporting
  - Image loading libraries (Coil)
  - Notification channels
  - Background sync workers

### 2. App Startup Library

We use AndroidX App Startup library to manage component initialization:

```kotlin
class CoilInitializer : BaseInitializer<Unit>() {
    override fun create(context: Context) {
        // Coil configuration happens lazily
    }
}
```

### 3. Startup Profiling

The `StartupProfiler` utility tracks initialization milestones:

```kotlin
StartupProfiler.markAppStart()
// ... initialization code ...
StartupProfiler.recordMilestone("Critical components initialized")
StartupProfiler.logStartupMetrics()
```

### 4. Performance Targets

- **Target**: App displays main screen within 2 seconds on Android 8.0+
- **Measurement**: Use `StartupProfiler.getStartupTime()` to verify
- **Validation**: `StartupProfiler.meetsPerformanceTarget()` returns true if under 2s

## Implementation in Concrete Apps

### Rider App Example

```kotlin
@HiltAndroidApp
class RiderApplication : BaseApplication() {
    
    override fun getSavedLanguage(): Language {
        // Get from SettingsRepository
        return Language.SYSTEM_DEFAULT
    }
    
    override fun initializeCriticalComponents() {
        super.initializeCriticalComponents()
        // Initialize critical Rider-specific components
    }
    
    override fun initializeNonCriticalComponents() {
        super.initializeNonCriticalComponents()
        // Initialize non-critical components asynchronously
        CoroutineScope(Dispatchers.Default).launch {
            // Firebase Crashlytics
            // Coil image loading
            // Notification channels
        }
    }
}
```

### Driver App Example

```kotlin
@HiltAndroidApp
class DriverApplication : BaseApplication() {
    
    override fun getSavedLanguage(): Language {
        // Get from SettingsRepository
        return Language.SYSTEM_DEFAULT
    }
    
    override fun initializeCriticalComponents() {
        super.initializeCriticalComponents()
        // Initialize critical Driver-specific components
    }
    
    override fun initializeNonCriticalComponents() {
        super.initializeNonCriticalComponents()
        // Initialize non-critical components asynchronously
    }
}
```

## Profiling and Debugging

### Enable Startup Profiling

Startup metrics are automatically logged in debug builds:

```
D/StartupProfiler: App start marked at 12345
D/StartupProfiler: Milestone 'Application.onCreate' reached at 50ms
D/StartupProfiler: Milestone 'Critical components initialized' reached at 150ms
I/StartupProfiler: === App Startup Metrics ===
I/StartupProfiler: Total startup time: 1800ms
I/StartupProfiler:   Application.onCreate: 50ms
I/StartupProfiler:   Critical components initialized: 150ms
I/StartupProfiler: ===========================
```

### Measure Startup Time

Use Android Studio's App Startup profiler:
1. Run > Profile 'app'
2. Select "Startup" profiler
3. Analyze initialization timeline
4. Identify bottlenecks

### Optimization Checklist

- [ ] Hilt dependency injection is configured correctly
- [ ] No blocking I/O operations in Application.onCreate()
- [ ] Database initialization is deferred until first use
- [ ] Network requests are not made during startup
- [ ] Image loading libraries use lazy initialization
- [ ] Notification channels are created on-demand
- [ ] Analytics and crash reporting initialize asynchronously
- [ ] Startup time is under 2 seconds on target devices

## Best Practices

1. **Avoid Blocking Operations**: Never perform network requests, database queries, or file I/O in Application.onCreate()

2. **Use Lazy Initialization**: Initialize components only when they're first needed

3. **Defer Background Work**: Use WorkManager for background tasks, not Application.onCreate()

4. **Profile Regularly**: Measure startup time on different devices and Android versions

5. **Monitor Regressions**: Set up CI/CD checks to catch startup time regressions

## Performance Targets by Device

| Device Category | Target Startup Time |
|----------------|---------------------|
| High-end (2021+) | < 1.5 seconds |
| Mid-range (2019-2020) | < 2.0 seconds |
| Low-end (2017-2018) | < 2.5 seconds |

## Related Requirements

- **Requirement 23.1**: App startup time within 2 seconds on Android 8.0+
