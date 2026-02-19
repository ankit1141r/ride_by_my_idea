# 📱 Android App Implementation Guide

## Overview

This guide provides step-by-step instructions for implementing the RideConnect Android applications. The project foundation is already set up - this guide will help you complete the implementation.

---

## 🎯 What's Already Done

✅ Project structure created  
✅ Gradle configuration complete  
✅ All dependencies configured  
✅ ProGuard rules set up  
✅ Multi-module architecture defined  

## 🚀 What Needs Implementation

This guide covers implementing **150+ source files** across **38 major tasks**.

---

## 📋 Implementation Roadmap

### Phase 1: Core Infrastructure (Days 1-5)
- Task 1: Complete project setup
- Task 2-3: Authentication module
- Task 4: Network layer
- Task 5: Database layer
- Task 6-7: Location services & Maps
- Task 8: WebSocket module

### Phase 2: Ride Management (Days 6-12)
- Task 10: Profile management
- Task 11: Ride request (Rider)
- Task 12: Scheduled rides
- Task 13: Parcel delivery
- Task 14-15: Driver features

### Phase 3: Additional Features (Days 13-18)
- Task 17: Payments
- Task 18: Ratings
- Task 19: Chat
- Task 20: Emergency features
- Task 21: Earnings (Driver)
- Task 22: Push notifications
- Task 23: Offline sync

### Phase 4: Polish (Days 19-25)
- UI/UX refinement
- Testing
- Performance optimization
- Bug fixes

---

## 🔧 Step-by-Step Implementation

### STEP 1: Complete Project Setup

#### 1.1 Create AndroidManifest.xml for Rider App

**File**: `rider-app/src/main/AndroidManifest.xml`

```xml
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:tools="http://schemas.android.com/tools">

    <!-- Permissions -->
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_FINE_LOCATION" />
    <uses-permission android:name="android.permission.ACCESS_COARSE_LOCATION" />
    <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />
    <uses-permission android:name="android.permission.USE_BIOMETRIC" />
    
    <uses-feature
        android:name="android.hardware.location.gps"
        android:required="false" />

    <application
        android:name=".RiderApp"
        android:allowBackup="true"
        android:dataExtractionRules="@xml/data_extraction_rules"
        android:fullBackupContent="@xml/backup_rules"
        android:icon="@mipmap/ic_launcher"
        android:label="@string/app_name"
        android:roundIcon="@mipmap/ic_launcher_round"
        android:supportsRtl="true"
        android:theme="@style/Theme.RideConnect"
        android:usesCleartextTraffic="true"
        tools:targetApi="31">
        
        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:theme="@style/Theme.RideConnect"
            android:windowSoftInputMode="adjustResize">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <!-- Google Maps API Key -->
        <meta-data
            android:name="com.google.android.geo.API_KEY"
            android:value="${MAPS_API_KEY}" />

        <!-- Firebase Messaging Service -->
        <service
            android:name=".service.RiderFirebaseMessagingService"
            android:exported="false">
            <intent-filter>
                <action android:name="com.google.firebase.MESSAGING_EVENT" />
            </intent-filter>
        </service>

    </application>

</manifest>
```

#### 1.2 Create Application Class

**File**: `rider-app/src/main/kotlin/com/rideconnect/rider/RiderApp.kt`

```kotlin
package com.rideconnect.rider

import android.app.Application
import dagger.hilt.android.HiltAndroidApp
import timber.log.Timber

@HiltAndroidApp
class RiderApp : Application() {
    
    override fun onCreate() {
        super.onCreate()
        
        // Initialize Timber for logging
        if (BuildConfig.DEBUG) {
            Timber.plant(Timber.DebugTree())
        }
        
        Timber.d("RiderApp initialized")
    }
}
```

#### 1.3 Create MainActivity

**File**: `rider-app/src/main/kotlin/com/rideconnect/rider/MainActivity.kt`

```kotlin
package com.rideconnect.rider

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.ui.Modifier
import com.rideconnect.rider.ui.theme.RideConnectTheme
import dagger.hilt.android.AndroidEntryPoint

@AndroidEntryPoint
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            RideConnectTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    // Navigation will be added here
                    // RiderNavGraph()
                }
            }
        }
    }
}
```

#### 1.4 Repeat for Driver App

Create similar files for `driver-app`:
- `driver-app/src/main/AndroidManifest.xml`
- `driver-app/src/main/kotlin/com/rideconnect/driver/DriverApp.kt`
- `driver-app/src/main/kotlin/com/rideconnect/driver/MainActivity.kt`

---

### STEP 2: Implement Core Domain Models

#### 2.1 Create Domain Models

**File**: `core/domain/src/main/kotlin/com/rideconnect/core/domain/model/User.kt`

```kotlin
package com.rideconnect.core.domain.model

import java.time.LocalDateTime

data class User(
    val id: String,
    val phoneNumber: String,
    val name: String,
    val email: String?,
    val profilePhotoUrl: String?,
    val userType: UserType,
    val rating: Double,
    val createdAt: LocalDateTime
)

enum class UserType {
    RIDER,
    DRIVER
}
```

**File**: `core/domain/src/main/kotlin/com/rideconnect/core/domain/model/Ride.kt`

```kotlin
package com.rideconnect.core.domain.model

import java.time.LocalDateTime

data class Ride(
    val id: String,
    val riderId: String,
    val driverId: String?,
    val pickupLocation: Location,
    val dropoffLocation: Location,
    val status: RideStatus,
    val fare: Double?,
    val distance: Double?,
    val duration: Int?,
    val requestedAt: LocalDateTime,
    val acceptedAt: LocalDateTime?,
    val startedAt: LocalDateTime?,
    val completedAt: LocalDateTime?,
    val cancelledAt: LocalDateTime?,
    val cancellationReason: String?
)

enum class RideStatus {
    REQUESTED,
    SEARCHING,
    ACCEPTED,
    DRIVER_ARRIVING,
    ARRIVED,
    IN_PROGRESS,
    COMPLETED,
    CANCELLED
}
```

**File**: `core/domain/src/main/kotlin/com/rideconnect/core/domain/model/Location.kt`

```kotlin
package com.rideconnect.core.domain.model

data class Location(
    val latitude: Double,
    val longitude: Double,
    val address: String?,
    val placeId: String?
)
```

Create similar models for:
- `AuthToken.kt`
- `Driver.kt`
- `Transaction.kt`
- `Rating.kt`
- `ScheduledRide.kt`
- `ParcelDelivery.kt`
- `ChatMessage.kt`
- `EmergencyContact.kt`

---

### STEP 3: Implement Network Layer

#### 3.1 Create API Interfaces

**File**: `core/network/src/main/kotlin/com/rideconnect/core/network/api/AuthApi.kt`

```kotlin
package com.rideconnect.core.network.api

import com.rideconnect.core.network.dto.AuthResponse
import com.rideconnect.core.network.dto.SendOtpRequest
import com.rideconnect.core.network.dto.VerifyOtpRequest
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.POST

interface AuthApi {
    
    @POST("auth/send-otp")
    suspend fun sendOtp(@Body request: SendOtpRequest): Response<Unit>
    
    @POST("auth/verify-otp")
    suspend fun verifyOtp(@Body request: VerifyOtpRequest): Response<AuthResponse>
    
    @POST("auth/logout")
    suspend fun logout(): Response<Unit>
}
```

**File**: `core/network/src/main/kotlin/com/rideconnect/core/network/api/RideApi.kt`

```kotlin
package com.rideconnect.core.network.api

import com.rideconnect.core.network.dto.RideRequest
import com.rideconnect.core.network.dto.RideResponse
import retrofit2.Response
import retrofit2.http.*

interface RideApi {
    
    @POST("rides/request")
    suspend fun requestRide(@Body request: RideRequest): Response<RideResponse>
    
    @GET("rides/history")
    suspend fun getRideHistory(
        @Query("page") page: Int,
        @Query("page_size") pageSize: Int
    ): Response<List<RideResponse>>
    
    @POST("rides/{rideId}/cancel")
    suspend fun cancelRide(
        @Path("rideId") rideId: String,
        @Body reason: Map<String, String>
    ): Response<Unit>
}
```

#### 3.2 Create DTOs (Data Transfer Objects)

**File**: `core/network/src/main/kotlin/com/rideconnect/core/network/dto/AuthDto.kt`

```kotlin
package com.rideconnect.core.network.dto

import com.google.gson.annotations.SerializedName

data class SendOtpRequest(
    @SerializedName("phone_number")
    val phoneNumber: String
)

data class VerifyOtpRequest(
    @SerializedName("phone_number")
    val phoneNumber: String,
    @SerializedName("otp")
    val otp: String
)

data class AuthResponse(
    @SerializedName("access_token")
    val accessToken: String,
    @SerializedName("refresh_token")
    val refreshToken: String,
    @SerializedName("token_type")
    val tokenType: String,
    @SerializedName("user")
    val user: UserDto
)

data class UserDto(
    @SerializedName("id")
    val id: String,
    @SerializedName("phone_number")
    val phoneNumber: String,
    @SerializedName("name")
    val name: String,
    @SerializedName("email")
    val email: String?,
    @SerializedName("user_type")
    val userType: String,
    @SerializedName("rating")
    val rating: Double
)
```

#### 3.3 Create Retrofit Module

**File**: `core/network/src/main/kotlin/com/rideconnect/core/network/di/NetworkModule.kt`

```kotlin
package com.rideconnect.core.network.di

import com.rideconnect.core.network.api.AuthApi
import com.rideconnect.core.network.api.RideApi
import com.rideconnect.core.network.interceptor.AuthInterceptor
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {
    
    private const val BASE_URL = "http://10.0.2.2:8000/api/"
    
    @Provides
    @Singleton
    fun provideOkHttpClient(
        authInterceptor: AuthInterceptor
    ): OkHttpClient {
        return OkHttpClient.Builder()
            .addInterceptor(authInterceptor)
            .addInterceptor(HttpLoggingInterceptor().apply {
                level = HttpLoggingInterceptor.Level.BODY
            })
            .connectTimeout(30, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .writeTimeout(30, TimeUnit.SECONDS)
            .build()
    }
    
    @Provides
    @Singleton
    fun provideRetrofit(okHttpClient: OkHttpClient): Retrofit {
        return Retrofit.Builder()
            .baseUrl(BASE_URL)
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
    }
    
    @Provides
    @Singleton
    fun provideAuthApi(retrofit: Retrofit): AuthApi {
        return retrofit.create(AuthApi::class.java)
    }
    
    @Provides
    @Singleton
    fun provideRideApi(retrofit: Retrofit): RideApi {
        return retrofit.create(RideApi::class.java)
    }
}
```

---

### STEP 4: Implement Database Layer

#### 4.1 Create Room Entities

**File**: `core/database/src/main/kotlin/com/rideconnect/core/database/entity/RideEntity.kt`

```kotlin
package com.rideconnect.core.database.entity

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "rides")
data class RideEntity(
    @PrimaryKey val id: String,
    val riderId: String,
    val driverId: String?,
    val pickupLatitude: Double,
    val pickupLongitude: Double,
    val pickupAddress: String?,
    val dropoffLatitude: Double,
    val dropoffLongitude: Double,
    val dropoffAddress: String?,
    val status: String,
    val fare: Double?,
    val distance: Double?,
    val duration: Int?,
    val requestedAt: Long,
    val acceptedAt: Long?,
    val startedAt: Long?,
    val completedAt: Long?,
    val cancelledAt: Long?,
    val cancellationReason: String?
)
```

#### 4.2 Create DAOs

**File**: `core/database/src/main/kotlin/com/rideconnect/core/database/dao/RideDao.kt`

```kotlin
package com.rideconnect.core.database.dao

import androidx.room.*
import com.rideconnect.core.database.entity.RideEntity
import kotlinx.coroutines.flow.Flow

@Dao
interface RideDao {
    
    @Query("SELECT * FROM rides WHERE riderId = :userId ORDER BY requestedAt DESC")
    fun getRideHistory(userId: String): Flow<List<RideEntity>>
    
    @Query("SELECT * FROM rides WHERE id = :rideId")
    suspend fun getRideById(rideId: String): RideEntity?
    
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertRide(ride: RideEntity)
    
    @Update
    suspend fun updateRide(ride: RideEntity)
    
    @Query("DELETE FROM rides WHERE id = :rideId")
    suspend fun deleteRide(rideId: String)
}
```

#### 4.3 Create Database

**File**: `core/database/src/main/kotlin/com/rideconnect/core/database/AppDatabase.kt`

```kotlin
package com.rideconnect.core.database

import androidx.room.Database
import androidx.room.RoomDatabase
import com.rideconnect.core.database.dao.RideDao
import com.rideconnect.core.database.entity.RideEntity

@Database(
    entities = [RideEntity::class],
    version = 1,
    exportSchema = false
)
abstract class AppDatabase : RoomDatabase() {
    abstract fun rideDao(): RideDao
}
```

---

### STEP 5: Implement Repository Pattern

#### 5.1 Create Repository Interface

**File**: `core/domain/src/main/kotlin/com/rideconnect/core/domain/repository/AuthRepository.kt`

```kotlin
package com.rideconnect.core.domain.repository

import com.rideconnect.core.domain.model.AuthToken
import com.rideconnect.core.domain.model.User

interface AuthRepository {
    suspend fun sendOtp(phoneNumber: String): Result<Unit>
    suspend fun verifyOtp(phoneNumber: String, otp: String): Result<AuthToken>
    suspend fun logout(): Result<Unit>
    fun getStoredToken(): AuthToken?
    suspend fun saveToken(token: AuthToken)
    suspend fun clearToken()
}
```

#### 5.2 Implement Repository

**File**: `core/data/src/main/kotlin/com/rideconnect/core/data/repository/AuthRepositoryImpl.kt`

```kotlin
package com.rideconnect.core.data.repository

import com.rideconnect.core.data.local.TokenManager
import com.rideconnect.core.domain.model.AuthToken
import com.rideconnect.core.domain.repository.AuthRepository
import com.rideconnect.core.network.api.AuthApi
import com.rideconnect.core.network.dto.SendOtpRequest
import com.rideconnect.core.network.dto.VerifyOtpRequest
import javax.inject.Inject

class AuthRepositoryImpl @Inject constructor(
    private val authApi: AuthApi,
    private val tokenManager: TokenManager
) : AuthRepository {
    
    override suspend fun sendOtp(phoneNumber: String): Result<Unit> {
        return try {
            val response = authApi.sendOtp(SendOtpRequest(phoneNumber))
            if (response.isSuccessful) {
                Result.success(Unit)
            } else {
                Result.failure(Exception("Failed to send OTP"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    override suspend fun verifyOtp(phoneNumber: String, otp: String): Result<AuthToken> {
        return try {
            val response = authApi.verifyOtp(VerifyOtpRequest(phoneNumber, otp))
            if (response.isSuccessful && response.body() != null) {
                val authResponse = response.body()!!
                val token = AuthToken(
                    accessToken = authResponse.accessToken,
                    refreshToken = authResponse.refreshToken,
                    tokenType = authResponse.tokenType
                )
                saveToken(token)
                Result.success(token)
            } else {
                Result.failure(Exception("Invalid OTP"))
            }
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    override suspend fun logout(): Result<Unit> {
        return try {
            authApi.logout()
            clearToken()
            Result.success(Unit)
        } catch (e: Exception) {
            Result.failure(e)
        }
    }
    
    override fun getStoredToken(): AuthToken? {
        return tokenManager.getToken()
    }
    
    override suspend fun saveToken(token: AuthToken) {
        tokenManager.saveToken(token)
    }
    
    override suspend fun clearToken() {
        tokenManager.clearToken()
    }
}
```

---

### STEP 6: Implement ViewModels

#### 6.1 Create AuthViewModel

**File**: `rider-app/src/main/kotlin/com/rideconnect/rider/viewmodel/AuthViewModel.kt`

```kotlin
package com.rideconnect.rider.viewmodel

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.rideconnect.core.domain.repository.AuthRepository
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class AuthViewModel @Inject constructor(
    private val authRepository: AuthRepository
) : ViewModel() {
    
    private val _authState = MutableStateFlow<AuthState>(AuthState.Initial)
    val authState: StateFlow<AuthState> = _authState.asStateFlow()
    
    fun sendOtp(phoneNumber: String) {
        viewModelScope.launch {
            _authState.value = AuthState.Loading
            authRepository.sendOtp(phoneNumber)
                .onSuccess {
                    _authState.value = AuthState.OtpSent
                }
                .onFailure { error ->
                    _authState.value = AuthState.Error(error.message ?: "Failed to send OTP")
                }
        }
    }
    
    fun verifyOtp(phoneNumber: String, otp: String) {
        viewModelScope.launch {
            _authState.value = AuthState.Loading
            authRepository.verifyOtp(phoneNumber, otp)
                .onSuccess { token ->
                    _authState.value = AuthState.Authenticated
                }
                .onFailure { error ->
                    _authState.value = AuthState.Error(error.message ?: "Invalid OTP")
                }
        }
    }
    
    fun logout() {
        viewModelScope.launch {
            authRepository.logout()
            _authState.value = AuthState.Initial
        }
    }
}

sealed class AuthState {
    object Initial : AuthState()
    object Loading : AuthState()
    object OtpSent : AuthState()
    object Authenticated : AuthState()
    data class Error(val message: String) : AuthState()
}
```

---

### STEP 7: Implement Compose UI

#### 7.1 Create Login Screen

**File**: `rider-app/src/main/kotlin/com/rideconnect/rider/ui/auth/LoginScreen.kt`

```kotlin
package com.rideconnect.rider.ui.auth

import androidx.compose.foundation.layout.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import com.rideconnect.rider.viewmodel.AuthViewModel
import com.rideconnect.rider.viewmodel.AuthState

@Composable
fun LoginScreen(
    viewModel: AuthViewModel = hiltViewModel(),
    onNavigateToOtp: () -> Unit,
    onNavigateToHome: () -> Unit
) {
    var phoneNumber by remember { mutableStateOf("") }
    val authState by viewModel.authState.collectAsState()
    
    LaunchedEffect(authState) {
        when (authState) {
            is AuthState.OtpSent -> onNavigateToOtp()
            is AuthState.Authenticated -> onNavigateToHome()
            else -> {}
        }
    }
    
    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Text(
            text = "Welcome to RideConnect",
            style = MaterialTheme.typography.headlineMedium
        )
        
        Spacer(modifier = Modifier.height(32.dp))
        
        OutlinedTextField(
            value = phoneNumber,
            onValueChange = { phoneNumber = it },
            label = { Text("Phone Number") },
            placeholder = { Text("+91 1234567890") },
            modifier = Modifier.fillMaxWidth()
        )
        
        Spacer(modifier = Modifier.height(16.dp))
        
        Button(
            onClick = { viewModel.sendOtp(phoneNumber) },
            modifier = Modifier.fillMaxWidth(),
            enabled = authState !is AuthState.Loading
        ) {
            if (authState is AuthState.Loading) {
                CircularProgressIndicator(
                    modifier = Modifier.size(24.dp),
                    color = MaterialTheme.colorScheme.onPrimary
                )
            } else {
                Text("Send OTP")
            }
        }
        
        if (authState is AuthState.Error) {
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = (authState as AuthState.Error).message,
                color = MaterialTheme.colorScheme.error
            )
        }
    }
}
```

---

## 📚 Additional Resources

### Key Files to Implement

1. **Core Domain** (15-20 files)
   - Models for all entities
   - Repository interfaces
   - Use cases

2. **Core Data** (20-25 files)
   - Repository implementations
   - Mappers (DTO ↔ Domain)
   - Local data sources

3. **Core Network** (25-30 files)
   - API interfaces
   - DTOs
   - Interceptors
   - WebSocket manager

4. **Core Database** (15-20 files)
   - Entities
   - DAOs
   - Database class
   - Migrations

5. **Rider App** (40-50 files)
   - ViewModels
   - Compose screens
   - Navigation
   - Services

6. **Driver App** (40-50 files)
   - Similar to Rider App
   - Driver-specific features

### Testing Strategy

1. **Unit Tests**: Test ViewModels, Repositories, Use Cases
2. **Integration Tests**: Test API calls, Database operations
3. **UI Tests**: Test Compose screens with Espresso

### Performance Tips

1. Use `LazyColumn` for lists
2. Implement pagination for ride history
3. Cache images with Coil
4. Use `remember` and `derivedStateOf` wisely
5. Optimize recomposition with `key()`

### Security Checklist

- ✅ Use EncryptedSharedPreferences for tokens
- ✅ Implement SSL pinning
- ✅ Validate all user inputs
- ✅ Use ProGuard for release builds
- ✅ Don't log sensitive data
- ✅ Implement biometric authentication

---

## 🎯 MVP Scope (If Time-Constrained)

Focus on these core features first:

**Rider App MVP:**
1. ✅ Phone authentication
2. ✅ Request immediate ride
3. ✅ View ride status
4. ✅ Basic map view
5. ✅ Cancel ride

**Driver App MVP:**
1. ✅ Phone authentication
2. ✅ Toggle availability
3. ✅ Receive ride requests
4. ✅ Accept/reject rides
5. ✅ Complete rides

**Skip for MVP:**
- Scheduled rides
- Parcel delivery
- Chat
- Ratings
- Earnings tracking
- Biometric auth

---

## 🆘 Common Issues & Solutions

### Issue: Gradle sync fails
**Solution**: Check JDK version (need 17), clear cache, restart Android Studio

### Issue: Cannot connect to backend
**Solution**: Use `10.0.2.2` for emulator, check backend is running

### Issue: Maps not showing
**Solution**: Add API key to `local.properties`, enable Maps SDK in Google Cloud

### Issue: Build errors
**Solution**: Clean project, rebuild, delete `.gradle` folder

---

## 📞 Need Help?

- Review the spec: `.kiro/specs/android-ride-hailing-app/`
- Check backend API docs: `http://localhost:8000/docs`
- Android documentation: https://developer.android.com
- Jetpack Compose: https://developer.android.com/jetpack/compose

---

**This guide provides the foundation. Continue implementing following the task list in `tasks.md`.**

**Good luck with the implementation! 🚀**
