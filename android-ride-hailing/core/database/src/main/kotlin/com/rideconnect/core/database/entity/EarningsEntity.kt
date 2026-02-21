package com.rideconnect.core.database.entity

import androidx.room.ColumnInfo
import androidx.room.Entity
import androidx.room.PrimaryKey

/**
 * Room entity for storing earnings data locally.
 * Requirements: 14.5, 14.6, 14.7
 */
@Entity(tableName = "earnings")
data class EarningsEntity(
    @PrimaryKey
    @ColumnInfo(name = "id")
    val id: String,
    
    @ColumnInfo(name = "driver_id")
    val driverId: String,
    
    @ColumnInfo(name = "ride_id")
    val rideId: String,
    
    @ColumnInfo(name = "date")
    val date: Long, // Timestamp in milliseconds
    
    @ColumnInfo(name = "fare")
    val fare: Double,
    
    @ColumnInfo(name = "pickup_address")
    val pickupAddress: String,
    
    @ColumnInfo(name = "dropoff_address")
    val dropoffAddress: String,
    
    @ColumnInfo(name = "distance")
    val distance: Double?,
    
    @ColumnInfo(name = "duration")
    val duration: Int?,
    
    @ColumnInfo(name = "is_pending")
    val isPending: Boolean = true,
    
    @ColumnInfo(name = "synced")
    val synced: Boolean = false,
    
    @ColumnInfo(name = "created_at")
    val createdAt: Long = System.currentTimeMillis()
)
