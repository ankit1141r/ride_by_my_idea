package com.rideconnect.core.database.entity

import androidx.room.ColumnInfo
import androidx.room.Entity
import androidx.room.Index
import androidx.room.PrimaryKey

@Entity(
    tableName = "scheduled_rides",
    indices = [
        Index(value = ["rider_id"]),
        Index(value = ["scheduled_time"]),
        Index(value = ["status"])
    ]
)
data class ScheduledRideEntity(
    @PrimaryKey
    @ColumnInfo(name = "id")
    val id: String,
    
    @ColumnInfo(name = "rider_id")
    val riderId: String,
    
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
    
    @ColumnInfo(name = "scheduled_time")
    val scheduledTime: Long,
    
    @ColumnInfo(name = "status")
    val status: String,
    
    @ColumnInfo(name = "created_at")
    val createdAt: Long
)
