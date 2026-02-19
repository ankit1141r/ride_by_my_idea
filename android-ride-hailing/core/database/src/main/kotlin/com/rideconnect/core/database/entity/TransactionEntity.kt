package com.rideconnect.core.database.entity

import androidx.room.ColumnInfo
import androidx.room.Entity
import androidx.room.Index
import androidx.room.PrimaryKey

@Entity(
    tableName = "transactions",
    indices = [
        Index(value = ["ride_id"]),
        Index(value = ["status"]),
        Index(value = ["created_at"])
    ]
)
data class TransactionEntity(
    @PrimaryKey
    @ColumnInfo(name = "id")
    val id: String,
    
    @ColumnInfo(name = "ride_id")
    val rideId: String,
    
    @ColumnInfo(name = "amount")
    val amount: Double,
    
    @ColumnInfo(name = "payment_method")
    val paymentMethod: String,
    
    @ColumnInfo(name = "status")
    val status: String,
    
    @ColumnInfo(name = "transaction_id")
    val transactionId: String?,
    
    @ColumnInfo(name = "created_at")
    val createdAt: Long,
    
    @ColumnInfo(name = "completed_at")
    val completedAt: Long?
)
