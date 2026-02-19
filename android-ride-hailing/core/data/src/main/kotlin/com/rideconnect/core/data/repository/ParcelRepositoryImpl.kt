package com.rideconnect.core.data.repository

import com.rideconnect.core.common.result.Result
import com.rideconnect.core.database.dao.ParcelDeliveryDao
import com.rideconnect.core.database.entity.ParcelDeliveryEntity
import com.rideconnect.core.domain.model.Location
import com.rideconnect.core.domain.model.ParcelDelivery
import com.rideconnect.core.domain.model.ParcelDeliveryRequest
import com.rideconnect.core.domain.model.ParcelSize
import com.rideconnect.core.domain.model.ParcelStatus
import com.rideconnect.core.domain.repository.ParcelRepository
import com.rideconnect.core.domain.websocket.WebSocketManager
import com.rideconnect.core.domain.websocket.WebSocketMessage
import com.rideconnect.core.network.api.ParcelApi
import com.rideconnect.core.network.dto.ParcelDeliveryRequestDto
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import java.text.SimpleDateFormat
import java.util.*
import javax.inject.Inject

/**
 * Implementation of ParcelRepository.
 * 
 * Requirements: 5.3, 5.6, 5.7, 15.3, 15.5, 15.7
 */
class ParcelRepositoryImpl @Inject constructor(
    private val parcelApi: ParcelApi,
    private val parcelDeliveryDao: ParcelDeliveryDao,
    private val webSocketManager: WebSocketManager
) : ParcelRepository {
    
    private val dateFormat = SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss'Z'", Locale.US).apply {
        timeZone = TimeZone.getTimeZone("UTC")
    }
    
    override suspend fun requestParcelDelivery(request: ParcelDeliveryRequest): Result<ParcelDelivery> {
        return try {
            val requestDto = ParcelDeliveryRequestDto(
                pickupLatitude = request.pickupLocation.latitude,
                pickupLongitude = request.pickupLocation.longitude,
                pickupAddress = request.pickupLocation.address,
                dropoffLatitude = request.dropoffLocation.latitude,
                dropoffLongitude = request.dropoffLocation.longitude,
                dropoffAddress = request.dropoffLocation.address,
                parcelSize = request.parcelSize.name,
                senderName = request.senderName,
                senderPhone = request.senderPhone,
                recipientName = request.recipientName,
                recipientPhone = request.recipientPhone,
                instructions = request.instructions
            )
            
            val response = parcelApi.requestParcelDelivery(requestDto)
            
            if (response.isSuccessful && response.body() != null) {
                val parcelDelivery = response.body()!!.toDomain()
                
                // Store in local database
                parcelDeliveryDao.insertParcelDelivery(parcelDelivery.toEntity())
                
                Result.Success(parcelDelivery)
            } else {
                Result.Error(Exception("Failed to request parcel delivery: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.Error(e)
        }
    }
    
    override suspend fun confirmPickup(deliveryId: String): Result<Unit> {
        return try {
            val response = parcelApi.confirmPickup(deliveryId)
            
            if (response.isSuccessful) {
                // Update local database
                parcelDeliveryDao.updateParcelStatus(deliveryId, ParcelStatus.PICKED_UP.name)
                Result.Success(Unit)
            } else {
                Result.Error(Exception("Failed to confirm pickup: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.Error(e)
        }
    }
    
    override suspend fun confirmDelivery(deliveryId: String): Result<Unit> {
        return try {
            val response = parcelApi.confirmDelivery(deliveryId)
            
            if (response.isSuccessful) {
                // Update local database
                parcelDeliveryDao.updateParcelStatus(deliveryId, ParcelStatus.DELIVERED.name)
                Result.Success(Unit)
            } else {
                Result.Error(Exception("Failed to confirm delivery: ${response.message()}"))
            }
        } catch (e: Exception) {
            Result.Error(e)
        }
    }
    
    override suspend fun getParcelHistory(page: Int, pageSize: Int): Result<List<ParcelDelivery>> {
        return try {
            val response = parcelApi.getParcelHistory(page, pageSize)
            
            if (response.isSuccessful && response.body() != null) {
                val parcels = response.body()!!.map { it.toDomain() }
                
                // Update local database
                parcels.forEach { parcel ->
                    parcelDeliveryDao.insertParcelDelivery(parcel.toEntity())
                }
                
                Result.Success(parcels)
            } else {
                // Return cached data if API fails
                val cachedParcels = parcelDeliveryDao.getAllParcelDeliveries()
                    .map { it.toDomain() }
                Result.Success(cachedParcels)
            }
        } catch (e: Exception) {
            // Return cached data on error
            try {
                val cachedParcels = parcelDeliveryDao.getAllParcelDeliveries()
                    .map { it.toDomain() }
                Result.Success(cachedParcels)
            } catch (dbError: Exception) {
                Result.Error(e)
            }
        }
    }
    
    override suspend fun getParcelDetails(deliveryId: String): Result<ParcelDelivery> {
        return try {
            // Try to get from local database first
            val cachedParcel = parcelDeliveryDao.getParcelDeliveryById(deliveryId)
            if (cachedParcel != null) {
                Result.Success(cachedParcel.toDomain())
            } else {
                Result.Error(Exception("Parcel delivery not found"))
            }
        } catch (e: Exception) {
            Result.Error(e)
        }
    }
    
    override fun observeActiveParcel(): Flow<ParcelDelivery?> {
        return parcelDeliveryDao.observeActiveParcelDelivery().map { entity ->
            entity?.toDomain()
        }
    }
    
    // Extension functions for mapping
    private fun com.rideconnect.core.network.dto.ParcelDeliveryResponseDto.toDomain(): ParcelDelivery {
        return ParcelDelivery(
            id = this.id,
            senderId = this.senderId,
            driverId = this.driverId,
            pickupLocation = Location(
                latitude = this.pickupLatitude,
                longitude = this.pickupLongitude,
                address = this.pickupAddress,
                accuracy = 0f,
                timestamp = System.currentTimeMillis()
            ),
            dropoffLocation = Location(
                latitude = this.dropoffLatitude,
                longitude = this.dropoffLongitude,
                address = this.dropoffAddress,
                accuracy = 0f,
                timestamp = System.currentTimeMillis()
            ),
            parcelSize = when (this.parcelSize.uppercase()) {
                "SMALL" -> ParcelSize.SMALL
                "MEDIUM" -> ParcelSize.MEDIUM
                "LARGE" -> ParcelSize.LARGE
                else -> ParcelSize.SMALL
            },
            senderName = this.senderName,
            senderPhone = this.senderPhone,
            recipientName = this.recipientName,
            recipientPhone = this.recipientPhone,
            instructions = this.instructions,
            status = when (this.status.uppercase()) {
                "REQUESTED" -> ParcelStatus.REQUESTED
                "ACCEPTED" -> ParcelStatus.ACCEPTED
                "PICKED_UP" -> ParcelStatus.PICKED_UP
                "IN_TRANSIT" -> ParcelStatus.IN_TRANSIT
                "DELIVERED" -> ParcelStatus.DELIVERED
                "CANCELLED" -> ParcelStatus.CANCELLED
                else -> ParcelStatus.REQUESTED
            },
            fare = this.fare,
            distance = null,
            requestedAt = try {
                dateFormat.parse(this.requestedAt)?.time ?: System.currentTimeMillis()
            } catch (e: Exception) {
                System.currentTimeMillis()
            },
            pickedUpAt = this.pickedUpAt?.let {
                try {
                    dateFormat.parse(it)?.time
                } catch (e: Exception) {
                    null
                }
            },
            deliveredAt = this.deliveredAt?.let {
                try {
                    dateFormat.parse(it)?.time
                } catch (e: Exception) {
                    null
                }
            }
        )
    }
    
    private fun ParcelDelivery.toEntity(): ParcelDeliveryEntity {
        return ParcelDeliveryEntity(
            id = this.id,
            senderId = this.senderId,
            driverId = this.driverId,
            pickupLatitude = this.pickupLocation.latitude,
            pickupLongitude = this.pickupLocation.longitude,
            pickupAddress = this.pickupLocation.address,
            dropoffLatitude = this.dropoffLocation.latitude,
            dropoffLongitude = this.dropoffLocation.longitude,
            dropoffAddress = this.dropoffLocation.address,
            parcelSize = this.parcelSize.name,
            senderName = this.senderName,
            senderPhone = this.senderPhone,
            recipientName = this.recipientName,
            recipientPhone = this.recipientPhone,
            instructions = this.instructions,
            status = this.status.name,
            fare = this.fare,
            requestedAt = this.requestedAt,
            pickedUpAt = this.pickedUpAt,
            deliveredAt = this.deliveredAt
        )
    }
    
    private fun ParcelDeliveryEntity.toDomain(): ParcelDelivery {
        return ParcelDelivery(
            id = this.id,
            senderId = this.senderId,
            driverId = this.driverId,
            pickupLocation = Location(
                latitude = this.pickupLatitude,
                longitude = this.pickupLongitude,
                address = this.pickupAddress,
                accuracy = 0f,
                timestamp = System.currentTimeMillis()
            ),
            dropoffLocation = Location(
                latitude = this.dropoffLatitude,
                longitude = this.dropoffLongitude,
                address = this.dropoffAddress,
                accuracy = 0f,
                timestamp = System.currentTimeMillis()
            ),
            parcelSize = ParcelSize.valueOf(this.parcelSize),
            senderName = this.senderName,
            senderPhone = this.senderPhone,
            recipientName = this.recipientName,
            recipientPhone = this.recipientPhone,
            instructions = this.instructions,
            status = ParcelStatus.valueOf(this.status),
            fare = this.fare,
            distance = null,
            requestedAt = this.requestedAt,
            pickedUpAt = this.pickedUpAt,
            deliveredAt = this.deliveredAt
        )
    }
}
