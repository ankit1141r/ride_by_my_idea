package com.rideconnect.core.network.di

import com.google.gson.Gson
import com.google.gson.GsonBuilder
import com.rideconnect.core.network.api.AuthApi
import com.rideconnect.core.network.api.DriverApi
import com.rideconnect.core.network.api.EmergencyApi
import com.rideconnect.core.network.api.LocationApi
import com.rideconnect.core.network.api.ParcelApi
import com.rideconnect.core.network.api.PaymentApi
import com.rideconnect.core.network.api.ProfileApi
import com.rideconnect.core.network.api.RatingApi
import com.rideconnect.core.network.api.RideApi
import com.rideconnect.core.network.api.ScheduledRideApi
import com.rideconnect.core.network.interceptor.AuthInterceptor
import com.rideconnect.core.network.interceptor.ErrorInterceptor
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.components.SingletonComponent
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.util.concurrent.TimeUnit
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object NetworkModule {
    
    private const val BASE_URL = "http://10.0.2.2:8000/api/"
    private const val API_TIMEOUT_SECONDS = 30L
    private const val UPLOAD_TIMEOUT_SECONDS = 60L
    
    @Provides
    @Singleton
    fun provideGson(): Gson {
        return GsonBuilder()
            .setDateFormat("yyyy-MM-dd'T'HH:mm:ss")
            .create()
    }
    
    @Provides
    @Singleton
    fun provideHttpLoggingInterceptor(): HttpLoggingInterceptor {
        return HttpLoggingInterceptor().apply {
            level = HttpLoggingInterceptor.Level.BODY
        }
    }
    
    @Provides
    @Singleton
    fun provideOkHttpClient(
        authInterceptor: AuthInterceptor,
        errorInterceptor: ErrorInterceptor,
        loggingInterceptor: HttpLoggingInterceptor
    ): OkHttpClient {
        return OkHttpClient.Builder()
            .addInterceptor(authInterceptor)
            .addInterceptor(errorInterceptor)
            .addInterceptor(loggingInterceptor)
            .connectTimeout(API_TIMEOUT_SECONDS, TimeUnit.SECONDS)
            .readTimeout(API_TIMEOUT_SECONDS, TimeUnit.SECONDS)
            .writeTimeout(API_TIMEOUT_SECONDS, TimeUnit.SECONDS)
            .build()
    }
    
    @Provides
    @Singleton
    fun provideUploadOkHttpClient(
        authInterceptor: AuthInterceptor,
        errorInterceptor: ErrorInterceptor,
        loggingInterceptor: HttpLoggingInterceptor
    ): OkHttpClient {
        return OkHttpClient.Builder()
            .addInterceptor(authInterceptor)
            .addInterceptor(errorInterceptor)
            .addInterceptor(loggingInterceptor)
            .connectTimeout(UPLOAD_TIMEOUT_SECONDS, TimeUnit.SECONDS)
            .readTimeout(UPLOAD_TIMEOUT_SECONDS, TimeUnit.SECONDS)
            .writeTimeout(UPLOAD_TIMEOUT_SECONDS, TimeUnit.SECONDS)
            .build()
    }
    
    @Provides
    @Singleton
    fun provideRetrofit(
        okHttpClient: OkHttpClient,
        gson: Gson
    ): Retrofit {
        return Retrofit.Builder()
            .baseUrl(BASE_URL)
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create(gson))
            .build()
    }
    
    @Provides
    @Singleton
    fun provideAuthApi(retrofit: Retrofit): AuthApi {
        return retrofit.create(AuthApi::class.java)
    }
    
    @Provides
    @Singleton
    fun provideRideApi(retrofit: Retrofit): RideApi {
        return retrofit.create(RideApi::class.java)
    }
    
    @Provides
    @Singleton
    fun provideDriverApi(retrofit: Retrofit): DriverApi {
        return retrofit.create(DriverApi::class.java)
    }
    
    @Provides
    @Singleton
    fun provideLocationApi(retrofit: Retrofit): LocationApi {
        return retrofit.create(LocationApi::class.java)
    }
    
    @Provides
    @Singleton
    fun providePaymentApi(retrofit: Retrofit): PaymentApi {
        return retrofit.create(PaymentApi::class.java)
    }
    
    @Provides
    @Singleton
    fun provideRatingApi(retrofit: Retrofit): RatingApi {
        return retrofit.create(RatingApi::class.java)
    }
    
    @Provides
    @Singleton
    fun provideParcelApi(retrofit: Retrofit): ParcelApi {
        return retrofit.create(ParcelApi::class.java)
    }
    
    @Provides
    @Singleton
    fun provideEmergencyApi(retrofit: Retrofit): EmergencyApi {
        return retrofit.create(EmergencyApi::class.java)
    }
    
    @Provides
    @Singleton
    fun provideProfileApi(retrofit: Retrofit): ProfileApi {
        return retrofit.create(ProfileApi::class.java)
    }
    
    @Provides
    @Singleton
    fun provideScheduledRideApi(retrofit: Retrofit): ScheduledRideApi {
        return retrofit.create(ScheduledRideApi::class.java)
    }
}
