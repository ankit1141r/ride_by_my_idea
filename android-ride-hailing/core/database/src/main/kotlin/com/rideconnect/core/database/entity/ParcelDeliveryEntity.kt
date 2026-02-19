package com.rideconnect.core.database.entity

import androidx.room.ColumnInfo
import androidx.room.Entity
import androidx.room.Index
import androidx.room.PrimaryKey

@Entity(
    tableName = "parcel_deliveries",
    indices = [
        Index(value = ["sender_id"]),
        Index(value = ["driver_id"]),
        Index(value = ["status"]),
        Index(value = ["requested_at"])
    ]
)
data class ParcelDeliveryEntity(
    @PrimaryKey
    @ColumnInfo(name = "id")
    val id: String,
    
    @ColumnInfo(name = "sender_id")
    val senderId: String,
    
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
    
    @ColumnInfo(name = "parcel_size")
    val parcelSize: String,
    
    @ColumnInfo(name = "sender_name")
    val senderName: String,
    
    @ColumnInfo(name = "sender_phone")
    val senderPhone: String,
    
    @ColumnInfo(name = "recipient_name")
    val recipientName: String,
    
    @ColumnInfo(name = "recipient_phone")
    val recipientPhone: String,
    
    @ColumnInfo(name = "instructions")
    val instructions: String?,
    
    @ColumnInfo(name = "status")
    val status: String,
    
    @ColumnInfo(name = "fare")
    val fare: Double?,
    
    @ColumnInfo(name = "requested_at")
    val requestedAt: Long,
    
    @ColumnInfo(name = "picked_up_at")
    val pickedUpAt: Long?,
    
    @ColumnInfo(name = "delivered_at")
    val deliveredAt: Long?
)
