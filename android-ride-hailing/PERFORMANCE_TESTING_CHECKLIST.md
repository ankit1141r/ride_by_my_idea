# Performance Testing Checklist

## Overview

This checklist guides you through performance testing for the Android Ride-Hailing Application. Complete each test and document the results.

---

## 1. App Startup Time Testing

### Cold Start Test
**Target:** < 3 seconds

**Steps:**
1. Force stop the app:
   ```bash
   adb shell am force-stop com.rideconnect.rider
   adb shell am force-stop com.rideconnect.driver
   ```

2. Launch and measure:
   ```bash
   adb shell am start -W com.rideconnect.rider/.MainActivity
   adb shell am start -W com.rideconnect.driver/.MainActivity
   ```

3. Look for `TotalTime` in the output

**Results:**
- [ ] Rider App Cold Start: _____ ms (Target: < 3000ms)
- [ ] Driver App Cold Start: _____ ms (Target: < 3000ms)

### Warm Start Test
**Target:** < 1 second

**Steps:**
1. Launch the app
2. Press home button
3. Reopen from recents
4. Measure time to interactive

**Results:**
- [ ] Rider App Warm Start: _____ ms (Target: < 1000ms)
- [ ] Driver App Warm Start: _____ ms (Target: < 1000ms)

### Hot Start Test
**Target:** < 500ms

**Steps:**
1. Launch the app
2. Press back to exit (don't force stop)
3. Relaunch immediately
4. Measure time to interactive

**Results:**
- [ ] Rider App Hot Start: _____ ms (Target: < 500ms)
- [ ] Driver App Hot Start: _____ ms (Target: < 500ms)

### Startup Profiling
**Tool:** Android Studio Profiler

**Steps:**
1. Open Android Studio Profiler
2. Select CPU profiler
3. Start recording
4. Launch the app
5. Stop recording when app is interactive
6. Analyze the trace

**Analysis:**
- [ ] Identify slow initialization methods
- [ ] Check for blocking operations on main thread
- [ ] Verify lazy initialization is working
- [ ] Document bottlenecks: _____________________

---

## 2. Memory Usage Testing

### Normal Usage Test
**Target:** < 200MB

**Steps:**
1. Launch the app
2. Navigate through main screens
3. Check memory usage:
   ```bash
   adb shell dumpsys meminfo com.rideconnect.rider
   adb shell dumpsys meminfo com.rideconnect.driver
   ```

**Results:**
- [ ] Rider App Normal Usage: _____ MB (Target: < 200MB)
- [ ] Driver App Normal Usage: _____ MB (Target: < 200MB)

### Peak Usage Test
**Target:** < 300MB

**Steps:**
1. Perform memory-intensive operations:
   - Load map with many markers
   - Load ride history (100+ rides)
   - Upload profile photo
   - Navigate rapidly between screens
2. Check memory usage

**Results:**
- [ ] Rider App Peak Usage: _____ MB (Target: < 300MB)
- [ ] Driver App Peak Usage: _____ MB (Target: < 300MB)

### Memory Leak Detection
**Tool:** Android Studio Memory Profiler

**Steps:**
1. Open Memory Profiler
2. Perform these actions 10 times:
   - Open and close a screen
   - Request and cancel a ride
   - Navigate to profile and back
3. Force GC after each iteration
4. Check for retained objects

**Results:**
- [ ] No Activity leaks detected
- [ ] No Fragment leaks detected
- [ ] No Bitmap leaks detected
- [ ] No Listener leaks detected
- [ ] Document any leaks found: _____________________

### Stress Test
**Duration:** 30 minutes

**Steps:**
1. Navigate through all screens repeatedly
2. Request and complete multiple rides (if possible)
3. Monitor memory over time
4. Check for memory growth

**Results:**
- [ ] Memory remains stable over 30 minutes
- [ ] No continuous memory growth
- [ ] App doesn't crash due to OOM
- [ ] Final memory usage: _____ MB

---

## 3. Battery Consumption Testing

### Rider App - Idle Test
**Target:** < 1% per hour

**Steps:**
1. Fully charge device
2. Reset battery stats:
   ```bash
   adb shell dumpsys batterystats --reset
   ```
3. Leave app idle for 1 hour
4. Check battery usage:
   ```bash
   adb shell dumpsys batterystats com.rideconnect.rider
   ```

**Results:**
- [ ] Battery drain: _____% per hour (Target: < 1%)

### Rider App - Active Ride Test
**Target:** < 5% per hour

**Steps:**
1. Reset battery stats
2. Simulate active ride for 1 hour:
   - Keep map visible
   - Track driver location
   - Receive location updates
3. Check battery usage

**Results:**
- [ ] Battery drain: _____% per hour (Target: < 5%)

### Driver App - Online Test
**Target:** < 10% per hour

**Steps:**
1. Reset battery stats
2. Set driver online for 1 hour:
   - Location tracking active
   - WebSocket connected
   - Waiting for ride requests
3. Check battery usage

**Results:**
- [ ] Battery drain: _____% per hour (Target: < 10%)

### Driver App - Offline Test
**Target:** < 1% per hour

**Steps:**
1. Reset battery stats
2. Keep driver offline for 1 hour
3. Check battery usage

**Results:**
- [ ] Battery drain: _____% per hour (Target: < 1%)

### Wake Lock Check

**Steps:**
1. Check for wake locks:
   ```bash
   adb shell dumpsys power
   ```
2. Verify no unnecessary wake locks

**Results:**
- [ ] No unnecessary wake locks detected
- [ ] Location wake lock only active when needed
- [ ] Document any issues: _____________________

### Energy Profiling
**Tool:** Android Studio Energy Profiler

**Steps:**
1. Open Energy Profiler
2. Profile for 10 minutes during typical usage
3. Identify energy-intensive operations

**Analysis:**
- [ ] Location update frequency is appropriate
- [ ] Network requests are batched
- [ ] No excessive CPU usage
- [ ] Document optimization opportunities: _____________________

---

## 4. Frame Rate Testing

### UI Animation Test
**Target:** 60 FPS

**Steps:**
1. Enable GPU rendering profile:
   - Settings → Developer Options → Profile GPU Rendering → On screen as bars
2. Test these animations:
   - Screen transitions
   - Bottom sheet animations
   - Dialog animations
   - Button press animations
3. Observe the bars (should stay below green line)

**Results:**
- [ ] Screen transitions: 60 FPS maintained
- [ ] Bottom sheet: 60 FPS maintained
- [ ] Dialogs: 60 FPS maintained
- [ ] Buttons: 60 FPS maintained
- [ ] Document any jank: _____________________

### Map Animation Test
**Target:** 60 FPS

**Steps:**
1. Enable GPU rendering profile
2. Test map animations:
   - Camera movements
   - Marker animations
   - Polyline drawing
   - Zoom in/out
3. Observe frame rate

**Results:**
- [ ] Camera movements: 60 FPS maintained
- [ ] Marker animations: 60 FPS maintained
- [ ] Polyline drawing: 60 FPS maintained
- [ ] Zoom operations: 60 FPS maintained
- [ ] Document any jank: _____________________

### Scrolling Test
**Target:** No jank

**Steps:**
1. Enable GPU rendering profile
2. Test scrolling in:
   - Ride history list
   - Payment history
   - Settings screen
   - Chat messages
3. Scroll rapidly and observe

**Results:**
- [ ] Ride history: Smooth scrolling
- [ ] Payment history: Smooth scrolling
- [ ] Settings: Smooth scrolling
- [ ] Chat: Smooth scrolling
- [ ] Document any jank: _____________________

### Compose Recomposition Profiling
**Tool:** Layout Inspector with Compose

**Steps:**
1. Open Layout Inspector
2. Enable "Show Recomposition Counts"
3. Interact with the app
4. Identify excessive recompositions

**Analysis:**
- [ ] No unnecessary recompositions detected
- [ ] State hoisting is correct
- [ ] Remember blocks are used appropriately
- [ ] Document optimization opportunities: _____________________

---

## 5. Network Performance Testing

### API Response Time Test

**Steps:**
1. Enable network profiling in Android Studio
2. Test these API calls:
   - Login (OTP send/verify)
   - Ride request
   - Location update
   - Payment processing
3. Measure response times

**Results:**
- [ ] Login: _____ ms (Target: < 1000ms)
- [ ] Ride request: _____ ms (Target: < 2000ms)
- [ ] Location update: _____ ms (Target: < 500ms)
- [ ] Payment: _____ ms (Target: < 3000ms)

### WebSocket Latency Test

**Steps:**
1. Connect WebSocket
2. Send location update
3. Measure time until acknowledgment
4. Repeat 100 times
5. Calculate average latency

**Results:**
- [ ] Average latency: _____ ms (Target: < 500ms)
- [ ] Max latency: _____ ms (Target: < 1000ms)
- [ ] 95th percentile: _____ ms

### Poor Network Conditions Test

**Steps:**
1. Use Network Profiler to simulate:
   - 3G connection
   - High latency (500ms)
   - Packet loss (5%)
2. Test critical flows
3. Verify retry logic works

**Results:**
- [ ] App remains responsive
- [ ] Retry logic activates correctly
- [ ] User feedback is clear
- [ ] No crashes or freezes
- [ ] Document any issues: _____________________

---

## 6. Database Performance Testing

### Query Performance Test

**Steps:**
1. Seed database with test data:
   - 1000 rides
   - 500 transactions
   - 100 chat messages
2. Measure query times:
   ```kotlin
   val startTime = System.currentTimeMillis()
   // Execute query
   val endTime = System.currentTimeMillis()
   Log.d("QueryTime", "Time: ${endTime - startTime}ms")
   ```

**Results:**
- [ ] Load ride history: _____ ms (Target: < 100ms)
- [ ] Load transactions: _____ ms (Target: < 100ms)
- [ ] Load chat messages: _____ ms (Target: < 50ms)
- [ ] Search rides: _____ ms (Target: < 200ms)

### Database Size Test

**Steps:**
1. Check database size:
   ```bash
   adb shell run-as com.rideconnect.rider ls -lh /data/data/com.rideconnect.rider/databases/
   ```
2. Verify reasonable size

**Results:**
- [ ] Database size: _____ MB
- [ ] Size is reasonable for data volume
- [ ] No excessive growth

---

## 7. Image Loading Performance

### Profile Photo Loading Test

**Steps:**
1. Load profile screen with photo
2. Measure load time
3. Check memory usage
4. Verify caching works

**Results:**
- [ ] First load: _____ ms
- [ ] Cached load: _____ ms (Target: < 100ms)
- [ ] Memory usage is reasonable
- [ ] Caching works correctly

### Image Compression Test

**Steps:**
1. Upload a large photo (5MB+)
2. Verify compression happens
3. Check compressed size
4. Verify quality is acceptable

**Results:**
- [ ] Original size: _____ MB
- [ ] Compressed size: _____ MB
- [ ] Compression ratio: _____ % (Target: ~50%)
- [ ] Quality is acceptable

---

## 8. Location Services Performance

### Location Update Frequency Test

**Steps:**
1. Enable location tracking
2. Monitor update frequency
3. Verify it matches configuration:
   - Normal: 10 seconds
   - SOS: 5 seconds

**Results:**
- [ ] Normal mode: _____ seconds between updates (Target: 10s)
- [ ] SOS mode: _____ seconds between updates (Target: 5s)
- [ ] Updates are consistent

### GPS Accuracy Test

**Steps:**
1. Test in different conditions:
   - Outdoors with clear sky
   - Indoors
   - Urban canyon
2. Check accuracy values

**Results:**
- [ ] Outdoors accuracy: _____ meters
- [ ] Indoors accuracy: _____ meters
- [ ] Urban accuracy: _____ meters
- [ ] Warnings shown when accuracy > 50m

---

## 9. Pagination Performance

### Ride History Pagination Test

**Steps:**
1. Load ride history with 1000+ rides
2. Scroll through list
3. Verify pagination works
4. Check memory usage

**Results:**
- [ ] Initial load: _____ items (Target: 20)
- [ ] Load time: _____ ms (Target: < 200ms)
- [ ] Smooth scrolling maintained
- [ ] Memory usage is stable
- [ ] Pagination triggers correctly

---

## 10. WebSocket Message Size Test

### Message Size Verification

**Steps:**
1. Monitor WebSocket messages
2. Check message sizes
3. Verify they're under limit

**Results:**
- [ ] Location update: _____ bytes (Target: < 10KB)
- [ ] Ride status: _____ bytes (Target: < 10KB)
- [ ] Chat message: _____ bytes (Target: < 10KB)
- [ ] All messages under 10KB limit

---

## Summary

### Overall Performance Rating

- [ ] **Excellent** - All targets met, no issues
- [ ] **Good** - Most targets met, minor issues
- [ ] **Fair** - Some targets missed, needs optimization
- [ ] **Poor** - Many targets missed, significant work needed

### Critical Issues Found

1. _____________________
2. _____________________
3. _____________________

### Optimization Priorities

1. _____________________
2. _____________________
3. _____________________

### Next Steps

- [ ] Address critical performance issues
- [ ] Implement recommended optimizations
- [ ] Re-test after optimizations
- [ ] Document performance benchmarks

---

**Testing Date:** _____________________
**Tested By:** _____________________
**Device(s) Used:** _____________________
**Android Version(s):** _____________________
