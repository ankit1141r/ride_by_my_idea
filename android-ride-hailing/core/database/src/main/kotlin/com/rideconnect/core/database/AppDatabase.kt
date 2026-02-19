package com.rideconnect.core.database

import androidx.room.Database
import androidx.room.RoomDatabase
import com.rideconnect.core.database.dao.*
import com.rideconnect.core.database.entity.*

@Database(
    entities = [
        UserEntity::class,
        RideEntity::class,
        ScheduledRideEntity::class,
        TransactionEntity::class,
        ChatMessageEntity::class,
        EmergencyContactEntity::class,
        ParcelDeliveryEntity::class,
        RatingEntity::class,
        PendingRatingEntity::class
    ],
    version = 1,
    exportSchema = true
)
abstract class AppDatabase : RoomDatabase() {
    abstract fun userDao(): UserDao
    abstract fun rideDao(): RideDao
    abstract fun scheduledRideDao(): ScheduledRideDao
    abstract fun transactionDao(): TransactionDao
    abstract fun chatMessageDao(): ChatMessageDao
    abstract fun emergencyContactDao(): EmergencyContactDao
    abstract fun parcelDeliveryDao(): ParcelDeliveryDao
    abstract fun ratingDao(): RatingDao
    
    companion object {
        const val DATABASE_NAME = "rideconnect_database"
    }
}
