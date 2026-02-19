package com.rideconnect.core.database.entity

import androidx.room.ColumnInfo
import androidx.room.Entity
import androidx.room.PrimaryKey

/**
 * Rating entity for Room database.
 * Requirements: 8.5, 8.6
 */
@Entity(tableName = "ratings")
data class RatingEntity(
    @PrimaryKey
    @ColumnInfo(name = "id")
    val id: String,
    
    @ColumnInfo(name = "ride_id")
    val rideId: String,
    
    @ColumnInfo(name = "rater_id")
    val raterId: String,
    
    @ColumnInfo(name = "rated_user_id")
    val ratedUserId: String,
    
    @ColumnInfo(name = "rating")
    val rating: Int,
    
    @ColumnInfo(name = "review")
    val review: String?,
    
    @ColumnInfo(name = "created_at")
    val createdAt: Long
)

/**
 * Pending rating entity for offline queue.
 * Requirements: 8.7
 */
@Entity(tableName = "pending_ratings")
data class PendingRatingEntity(
    @PrimaryKey
    @ColumnInfo(name = "ride_id")
    val rideId: String,
    
    @ColumnInfo(name = "rating")
    val rating: Int,
    
    @ColumnInfo(name = "review")
    val review: String?,
    
    @ColumnInfo(name = "created_at")
    val createdAt: Long
)
