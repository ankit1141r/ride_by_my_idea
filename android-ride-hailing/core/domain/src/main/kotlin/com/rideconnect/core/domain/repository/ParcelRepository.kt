package com.rideconnect.core.domain.repository

import com.rideconnect.core.common.result.Result
import com.rideconnect.core.domain.model.ParcelDelivery
import com.rideconnect.core.domain.model.ParcelDeliveryRequest
import kotlinx.coroutines.flow.Flow

/**
 * Repository interface for parcel delivery operations.
 * 
 * Requirements: 5.3, 5.6, 5.7, 15.3, 15.5, 15.7
 */
interface ParcelRepository {
    
    /**
     * Request a parcel delivery.
     * Requirements: 5.3
     */
    suspend fun requestParcelDelivery(request: ParcelDeliveryRequest): Result<ParcelDelivery>
    
    /**
     * Confirm parcel pickup by driver.
     * Requirements: 15.5
     */
    suspend fun confirmPickup(deliveryId: String): Result<Unit>
    
    /**
     * Confirm parcel delivery completion.
     * Requirements: 15.7
     */
    suspend fun confirmDelivery(deliveryId: String): Result<Unit>
    
    /**
     * Get parcel delivery history.
     * Requirements: 5.3
     */
    suspend fun getParcelHistory(page: Int = 0, pageSize: Int = 20): Result<List<ParcelDelivery>>
    
    /**
     * Get details of a specific parcel delivery.
     */
    suspend fun getParcelDetails(deliveryId: String): Result<ParcelDelivery>
    
    /**
     * Observe active parcel delivery.
     * Requirements: 5.6, 5.7
     */
    fun observeActiveParcel(): Flow<ParcelDelivery?>
}
