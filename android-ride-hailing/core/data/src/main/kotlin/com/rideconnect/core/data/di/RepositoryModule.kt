package com.rideconnect.core.data.di

import com.rideconnect.core.data.biometric.BiometricAuthManagerImpl
import com.rideconnect.core.data.location.GooglePlacesClient
import com.rideconnect.core.data.location.LocationRepositoryImpl
import com.rideconnect.core.data.location.LocationServiceImpl
import com.rideconnect.core.data.location.PlacesClient
import com.rideconnect.core.data.repository.AuthRepositoryImpl
import com.rideconnect.core.data.repository.ParcelRepositoryImpl
import com.rideconnect.core.data.repository.ProfileRepositoryImpl
import com.rideconnect.core.data.repository.RideRepositoryImpl
import com.rideconnect.core.data.repository.ScheduledRideRepositoryImpl
import com.rideconnect.core.data.websocket.WebSocketManagerImpl
import com.rideconnect.core.domain.biometric.BiometricAuthManager
import com.rideconnect.core.domain.location.LocationRepository
import com.rideconnect.core.domain.location.LocationService
import com.rideconnect.core.domain.repository.AuthRepository
import com.rideconnect.core.domain.repository.ParcelRepository
import com.rideconnect.core.domain.repository.ProfileRepository
import com.rideconnect.core.domain.repository.RideRepository
import com.rideconnect.core.domain.repository.ScheduledRideRepository
import com.rideconnect.core.domain.websocket.WebSocketManager
import dagger.Binds
import dagger.Module
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
abstract class RepositoryModule {
    
    @Binds
    @Singleton
    abstract fun bindAuthRepository(
        authRepositoryImpl: AuthRepositoryImpl
    ): AuthRepository
    
    @Binds
    @Singleton
    abstract fun bindBiometricAuthManager(
        biometricAuthManagerImpl: BiometricAuthManagerImpl
    ): BiometricAuthManager
    
    @Binds
    @Singleton
    abstract fun bindLocationService(
        locationServiceImpl: LocationServiceImpl
    ): LocationService
    
    @Binds
    @Singleton
    abstract fun bindLocationRepository(
        locationRepositoryImpl: LocationRepositoryImpl
    ): LocationRepository
    
    @Binds
    @Singleton
    abstract fun bindPlacesClient(
        googlePlacesClient: GooglePlacesClient
    ): PlacesClient
    
    @Binds
    @Singleton
    abstract fun bindWebSocketManager(
        webSocketManagerImpl: WebSocketManagerImpl
    ): WebSocketManager
    
    @Binds
    @Singleton
    abstract fun bindProfileRepository(
        profileRepositoryImpl: ProfileRepositoryImpl
    ): ProfileRepository
    
    @Binds
    @Singleton
    abstract fun bindRideRepository(
        rideRepositoryImpl: RideRepositoryImpl
    ): RideRepository
    
    @Binds
    @Singleton
    abstract fun bindScheduledRideRepository(
        scheduledRideRepositoryImpl: ScheduledRideRepositoryImpl
    ): ScheduledRideRepository
    
    @Binds
    @Singleton
    abstract fun bindParcelRepository(
        parcelRepositoryImpl: ParcelRepositoryImpl
    ): ParcelRepository
}
