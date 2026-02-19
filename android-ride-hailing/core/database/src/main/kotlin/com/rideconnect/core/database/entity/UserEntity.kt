package com.rideconnect.core.database.entity

import androidx.room.ColumnInfo
import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "users")
data class UserEntity(
    @PrimaryKey
    @ColumnInfo(name = "id")
    val id: String,
    
    @ColumnInfo(name = "phone_number")
    val phoneNumber: String,
    
    @ColumnInfo(name = "name")
    val name: String,
    
    @ColumnInfo(name = "email")
    val email: String?,
    
    @ColumnInfo(name = "profile_photo_url")
    val profilePhotoUrl: String?,
    
    @ColumnInfo(name = "user_type")
    val userType: String,
    
    @ColumnInfo(name = "rating")
    val rating: Double,
    
    @ColumnInfo(name = "created_at")
    val createdAt: Long
)
