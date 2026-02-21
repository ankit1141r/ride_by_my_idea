package com.rideconnect.core.common.map

import android.content.Context
import com.google.android.gms.maps.GoogleMap
import com.google.android.gms.maps.model.TileOverlayOptions
import com.google.android.gms.maps.model.UrlTileProvider
import java.io.File
import java.io.FileInputStream
import java.io.FileOutputStream
import java.net.URL

/**
 * Configuration for map tile caching
 * Requirements: 23.4
 */
object MapTileCacheConfig {
    
    private const val TILE_CACHE_DIR = "map_tiles"
    private const val MAX_CACHE_SIZE_MB = 50L
    
    /**
     * Get tile cache directory
     */
    fun getTileCacheDir(context: Context): File {
        val cacheDir = File(context.cacheDir, TILE_CACHE_DIR)
        if (!cacheDir.exists()) {
            cacheDir.mkdirs()
        }
        return cacheDir
    }
    
    /**
     * Clear tile cache if it exceeds maximum size
     * Requirements: 23.4
     */
    fun clearTileCacheIfNeeded(context: Context) {
        val cacheDir = getTileCacheDir(context)
        val cacheSize = calculateDirectorySize(cacheDir)
        val maxSizeBytes = MAX_CACHE_SIZE_MB * 1024 * 1024
        
        if (cacheSize > maxSizeBytes) {
            // Delete oldest files until under limit
            val files = cacheDir.listFiles()?.sortedBy { it.lastModified() } ?: return
            var currentSize = cacheSize
            
            for (file in files) {
                if (currentSize <= maxSizeBytes) break
                currentSize -= file.length()
                file.delete()
            }
        }
    }
    
    /**
     * Calculate total size of directory
     */
    private fun calculateDirectorySize(directory: File): Long {
        var size = 0L
        directory.listFiles()?.forEach { file ->
            size += if (file.isDirectory) {
                calculateDirectorySize(file)
            } else {
                file.length()
            }
        }
        return size
    }
    
    /**
     * Get cached tile or download if not available
     */
    fun getCachedTile(context: Context, x: Int, y: Int, zoom: Int, tileUrl: String): ByteArray? {
        val cacheDir = getTileCacheDir(context)
        val tileFile = File(cacheDir, "tile_${zoom}_${x}_${y}.png")
        
        return if (tileFile.exists()) {
            // Return cached tile
            FileInputStream(tileFile).use { it.readBytes() }
        } else {
            // Download and cache tile
            try {
                val url = URL(tileUrl)
                val tileData = url.readBytes()
                
                // Save to cache
                FileOutputStream(tileFile).use { it.write(tileData) }
                
                // Clean cache if needed
                clearTileCacheIfNeeded(context)
                
                tileData
            } catch (e: Exception) {
                null
            }
        }
    }
    
    /**
     * Create cached tile provider
     * Requirements: 23.4
     */
    fun createCachedTileProvider(context: Context): UrlTileProvider {
        return object : UrlTileProvider(256, 256) {
            override fun getTileUrl(x: Int, y: Int, zoom: Int): URL? {
                // Return null to use default Google Maps tiles
                // This is a placeholder for custom tile caching
                return null
            }
        }
    }
    
    /**
     * Clear all cached tiles
     */
    fun clearAllTiles(context: Context) {
        val cacheDir = getTileCacheDir(context)
        cacheDir.listFiles()?.forEach { it.delete() }
    }
    
    /**
     * Get cache statistics
     */
    fun getCacheStats(context: Context): CacheStats {
        val cacheDir = getTileCacheDir(context)
        val files = cacheDir.listFiles() ?: emptyArray()
        val totalSize = calculateDirectorySize(cacheDir)
        
        return CacheStats(
            fileCount = files.size,
            totalSizeBytes = totalSize,
            totalSizeMB = totalSize / (1024.0 * 1024.0)
        )
    }
    
    data class CacheStats(
        val fileCount: Int,
        val totalSizeBytes: Long,
        val totalSizeMB: Double
    )
}
