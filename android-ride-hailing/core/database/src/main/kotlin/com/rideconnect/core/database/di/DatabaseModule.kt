package com.rideconnect.core.database.di

import android.content.Context
import androidx.room.Room
import com.rideconnect.core.database.AppDatabase
import com.rideconnect.core.database.dao.*
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object DatabaseModule {
    
    @Provides
    @Singleton
    fun provideAppDatabase(
        @ApplicationContext context: Context
    ): AppDatabase {
        return Room.databaseBuilder(
            context,
            AppDatabase::class.java,
            AppDatabase.DATABASE_NAME
        )
            .fallbackToDestructiveMigration() // For development - replace with proper migrations in production
            .build()
    }
    
    @Provides
    @Singleton
    fun provideUserDao(database: AppDatabase): UserDao {
        return database.userDao()
    }
    
    @Provides
    @Singleton
    fun provideRideDao(database: AppDatabase): RideDao {
        return database.rideDao()
    }
    
    @Provides
    @Singleton
    fun provideScheduledRideDao(database: AppDatabase): ScheduledRideDao {
        return database.scheduledRideDao()
    }
    
    @Provides
    @Singleton
    fun provideTransactionDao(database: AppDatabase): TransactionDao {
        return database.transactionDao()
    }
    
    @Provides
    @Singleton
    fun provideChatMessageDao(database: AppDatabase): ChatMessageDao {
        return database.chatMessageDao()
    }
    
    @Provides
    @Singleton
    fun provideEmergencyContactDao(database: AppDatabase): EmergencyContactDao {
        return database.emergencyContactDao()
    }
    
    @Provides
    @Singleton
    fun provideParcelDeliveryDao(database: AppDatabase): ParcelDeliveryDao {
        return database.parcelDeliveryDao()
    }
}
