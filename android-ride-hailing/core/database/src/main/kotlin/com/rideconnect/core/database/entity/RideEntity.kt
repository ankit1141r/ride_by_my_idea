package com.rideconnect.core.database.entity

import androidx.room.ColumnInfo
import androidx.room.Entity
import androidx.room.Index
import androidx.room.PrimaryKey

@Entity(
    tableName = "rides",
    indices = [
        Index(value = ["rider_id"]),
        Index(value = ["driver_id"]),
        Index(value = ["status"]),
        Index(value = ["requested_at"])
    ]
)
data class RideEntity(
    @PrimaryKey
    @ColumnInfo(name = "id")
    val id: String,
    
    @ColumnInfo(name = "rider_id")
    val riderId: String,
    
    @ColumnInfo(name = "driver_id")
    val driverId: String?,
    
    @ColumnInfo(name = "pickup_latitude")
    val pickupLatitude: Double,
    
    @ColumnInfo(name = "pickup_longitude")
    val pickupLongitude: Double,
    
    @ColumnInfo(name = "pickup_address")
    val pickupAddress: String?,
    
    @ColumnInfo(name = "dropoff_latitude")
    val dropoffLatitude: Double,
    
    @ColumnInfo(name = "dropoff_longitude")
    val dropoffLongitude: Double,
    
    @ColumnInfo(name = "dropoff_address")
    val dropoffAddress: String?,
    
    @ColumnInfo(name = "status")
    val status: String,
    
    @ColumnInfo(name = "fare")
    val fare: Double?,
    
    @ColumnInfo(name = "distance")
    val distance: Double?,
    
    @ColumnInfo(name = "duration")
    val duration: Int?,
    
    @ColumnInfo(name = "requested_at")
    val requestedAt: Long,
    
    @ColumnInfo(name = "accepted_at")
    val acceptedAt: Long?,
    
    @ColumnInfo(name = "started_at")
    val startedAt: Long?,
    
    @ColumnInfo(name = "completed_at")
    val completedAt: Long?,
    
    @ColumnInfo(name = "cancelled_at")
    val cancelledAt: Long?,
    
    @ColumnInfo(name = "cancellation_reason")
    val cancellationReason: String?
)
