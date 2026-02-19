package com.rideconnect.core.domain.repository

import com.rideconnect.core.common.result.Result
import com.rideconnect.core.domain.model.FareEstimate
import com.rideconnect.core.domain.model.Ride
import com.rideconnect.core.domain.model.RideRequest
import kotlinx.coroutines.flow.Flow

interface RideRepository {
    
    suspend fun requestRide(request: RideRequest): Result<Ride>
    
    suspend fun getFareEstimate(request: RideRequest): Result<FareEstimate>
    
    suspend fun cancelRide(rideId: String, reason: String): Result<Unit>
    
    suspend fun getRideDetails(rideId: String): Result<Ride>
    
    suspend fun getRideHistory(page: Int, pageSize: Int): Result<List<Ride>>
    
    fun observeActiveRide(): Flow<Ride?>
    
    suspend fun setActiveRide(ride: Ride?)
}
