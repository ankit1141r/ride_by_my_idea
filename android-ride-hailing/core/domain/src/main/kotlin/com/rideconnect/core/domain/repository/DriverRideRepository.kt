package com.rideconnect.core.domain.repository

import com.rideconnect.core.common.result.Result
import com.rideconnect.core.domain.model.Ride
import kotlinx.coroutines.flow.Flow

interface DriverRideRepository {
    suspend fun setAvailability(isAvailable: Boolean): Result<Unit>
    suspend fun acceptRide(rideId: String): Result<Ride>
    suspend fun rejectRide(rideId: String, reason: String): Result<Unit>
    suspend fun startRide(rideId: String): Result<Unit>
    suspend fun completeRide(rideId: String): Result<Unit>
    suspend fun cancelRide(rideId: String, reason: String): Result<Unit>
    fun observeRideRequests(): Flow<Ride?>
    fun observeActiveRide(): Flow<Ride?>
}
