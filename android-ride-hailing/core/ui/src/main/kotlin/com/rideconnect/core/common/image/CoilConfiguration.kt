package com.rideconnect.core.common.image

import android.content.Context
import coil.ImageLoader
import coil.disk.DiskCache
import coil.memory.MemoryCache
import coil.request.CachePolicy
import coil.util.DebugLogger
import okhttp3.OkHttpClient
import java.util.concurrent.TimeUnit

/**
 * Configuration for Coil image loading library
 * Requirements: 23.3, 23.4
 */
object CoilConfiguration {
    
    private const val MEMORY_CACHE_SIZE_PERCENT = 0.25 // 25% of available memory
    private const val DISK_CACHE_SIZE_MB = 100L // 100 MB disk cache
    private const val DISK_CACHE_DIR = "image_cache"
    
    /**
     * Create optimized ImageLoader for the app
     * Requirements: 23.3, 23.4
     */
    fun createImageLoader(context: Context, debug: Boolean = false): ImageLoader {
        return ImageLoader.Builder(context)
            .memoryCache {
                MemoryCache.Builder(context)
                    .maxSizePercent(MEMORY_CACHE_SIZE_PERCENT)
                    .build()
            }
            .diskCache {
                DiskCache.Builder()
                    .directory(context.cacheDir.resolve(DISK_CACHE_DIR))
                    .maxSizeBytes(DISK_CACHE_SIZE_MB * 1024 * 1024)
                    .build()
            }
            .okHttpClient {
                OkHttpClient.Builder()
                    .connectTimeout(30, TimeUnit.SECONDS)
                    .readTimeout(30, TimeUnit.SECONDS)
                    .writeTimeout(30, TimeUnit.SECONDS)
                    .build()
            }
            .respectCacheHeaders(false) // Use our own cache policy
            .apply {
                if (debug) {
                    logger(DebugLogger())
                }
            }
            .build()
    }
    
    /**
     * Get cache policy for different image types
     */
    fun getCachePolicy(imageType: ImageType): CachePolicy {
        return when (imageType) {
            ImageType.PROFILE_PHOTO -> CachePolicy.ENABLED
            ImageType.VEHICLE_PHOTO -> CachePolicy.ENABLED
            ImageType.MAP_MARKER -> CachePolicy.ENABLED
            ImageType.TEMPORARY -> CachePolicy.DISABLED
        }
    }
    
    enum class ImageType {
        PROFILE_PHOTO,
        VEHICLE_PHOTO,
        MAP_MARKER,
        TEMPORARY
    }
}
