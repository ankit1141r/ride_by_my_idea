package com.rideconnect.core.common.util

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.graphics.Matrix
import android.media.ExifInterface
import android.net.Uri
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext
import java.io.ByteArrayOutputStream
import java.io.File
import java.io.FileOutputStream
import kotlin.math.min

/**
 * Utility for image compression and optimization
 * Requirements: 2.3, 23.3
 */
object ImageCompressionUtil {
    
    private const val MAX_IMAGE_DIMENSION = 1920 // Max width or height
    private const val COMPRESSION_QUALITY = 85 // JPEG quality (0-100)
    private const val TARGET_COMPRESSION_RATIO = 0.5 // 50% size reduction
    
    /**
     * Compress image from URI and save to file
     * Requirements: 2.3, 23.3
     * 
     * @param context Android context
     * @param imageUri Source image URI
     * @param outputFile Destination file
     * @return Compression ratio achieved (0.0 to 1.0)
     */
    suspend fun compressImage(
        context: Context,
        imageUri: Uri,
        outputFile: File
    ): Float = withContext(Dispatchers.IO) {
        try {
            // Get original file size
            val originalSize = context.contentResolver.openInputStream(imageUri)?.use { input ->
                input.available().toLong()
            } ?: 0L
            
            // Decode image with inSampleSize for memory efficiency
            val bitmap = decodeSampledBitmap(context, imageUri, MAX_IMAGE_DIMENSION, MAX_IMAGE_DIMENSION)
                ?: return@withContext 0f
            
            // Rotate image if needed based on EXIF data
            val rotatedBitmap = rotateImageIfRequired(context, bitmap, imageUri)
            
            // Compress and save
            FileOutputStream(outputFile).use { output ->
                rotatedBitmap.compress(Bitmap.CompressFormat.JPEG, COMPRESSION_QUALITY, output)
            }
            
            // Clean up
            if (rotatedBitmap != bitmap) {
                rotatedBitmap.recycle()
            }
            bitmap.recycle()
            
            // Calculate compression ratio
            val compressedSize = outputFile.length()
            val ratio = compressedSize.toFloat() / originalSize.toFloat()
            
            ratio
        } catch (e: Exception) {
            e.printStackTrace()
            0f
        }
    }
    
    /**
     * Compress image to byte array
     * 
     * @param context Android context
     * @param imageUri Source image URI
     * @return Compressed image as byte array
     */
    suspend fun compressImageToByteArray(
        context: Context,
        imageUri: Uri
    ): ByteArray? = withContext(Dispatchers.IO) {
        try {
            val bitmap = decodeSampledBitmap(context, imageUri, MAX_IMAGE_DIMENSION, MAX_IMAGE_DIMENSION)
                ?: return@withContext null
            
            val rotatedBitmap = rotateImageIfRequired(context, bitmap, imageUri)
            
            val outputStream = ByteArrayOutputStream()
            rotatedBitmap.compress(Bitmap.CompressFormat.JPEG, COMPRESSION_QUALITY, outputStream)
            
            if (rotatedBitmap != bitmap) {
                rotatedBitmap.recycle()
            }
            bitmap.recycle()
            
            outputStream.toByteArray()
        } catch (e: Exception) {
            e.printStackTrace()
            null
        }
    }
    
    /**
     * Decode bitmap with sampling to reduce memory usage
     */
    private fun decodeSampledBitmap(
        context: Context,
        imageUri: Uri,
        reqWidth: Int,
        reqHeight: Int
    ): Bitmap? {
        return context.contentResolver.openInputStream(imageUri)?.use { input ->
            // First decode with inJustDecodeBounds=true to check dimensions
            val options = BitmapFactory.Options().apply {
                inJustDecodeBounds = true
            }
            BitmapFactory.decodeStream(input, null, options)
            
            // Calculate inSampleSize
            options.inSampleSize = calculateInSampleSize(options, reqWidth, reqHeight)
            
            // Decode bitmap with inSampleSize set
            options.inJustDecodeBounds = false
            
            context.contentResolver.openInputStream(imageUri)?.use { inputStream ->
                BitmapFactory.decodeStream(inputStream, null, options)
            }
        }
    }
    
    /**
     * Calculate sample size for bitmap decoding
     */
    private fun calculateInSampleSize(
        options: BitmapFactory.Options,
        reqWidth: Int,
        reqHeight: Int
    ): Int {
        val height = options.outHeight
        val width = options.outWidth
        var inSampleSize = 1
        
        if (height > reqHeight || width > reqWidth) {
            val halfHeight = height / 2
            val halfWidth = width / 2
            
            // Calculate the largest inSampleSize value that is a power of 2
            while ((halfHeight / inSampleSize) >= reqHeight &&
                (halfWidth / inSampleSize) >= reqWidth
            ) {
                inSampleSize *= 2
            }
        }
        
        return inSampleSize
    }
    
    /**
     * Rotate image based on EXIF orientation
     */
    private fun rotateImageIfRequired(
        context: Context,
        bitmap: Bitmap,
        imageUri: Uri
    ): Bitmap {
        val input = context.contentResolver.openInputStream(imageUri) ?: return bitmap
        
        val exif = try {
            ExifInterface(input)
        } catch (e: Exception) {
            return bitmap
        } finally {
            input.close()
        }
        
        val orientation = exif.getAttributeInt(
            ExifInterface.TAG_ORIENTATION,
            ExifInterface.ORIENTATION_NORMAL
        )
        
        return when (orientation) {
            ExifInterface.ORIENTATION_ROTATE_90 -> rotateImage(bitmap, 90f)
            ExifInterface.ORIENTATION_ROTATE_180 -> rotateImage(bitmap, 180f)
            ExifInterface.ORIENTATION_ROTATE_270 -> rotateImage(bitmap, 270f)
            else -> bitmap
        }
    }
    
    /**
     * Rotate bitmap by specified degrees
     */
    private fun rotateImage(bitmap: Bitmap, degrees: Float): Bitmap {
        val matrix = Matrix().apply {
            postRotate(degrees)
        }
        return Bitmap.createBitmap(bitmap, 0, 0, bitmap.width, bitmap.height, matrix, true)
    }
    
    /**
     * Check if compression meets target ratio (50% reduction)
     * Requirements: 23.3
     */
    fun meetsCompressionTarget(compressionRatio: Float): Boolean {
        return compressionRatio <= TARGET_COMPRESSION_RATIO
    }
    
    /**
     * Get recommended image dimensions based on use case
     */
    fun getRecommendedDimensions(useCase: ImageUseCase): Pair<Int, Int> {
        return when (useCase) {
            ImageUseCase.PROFILE_PHOTO -> 512 to 512
            ImageUseCase.VEHICLE_DOCUMENT -> 1920 to 1920
            ImageUseCase.RECEIPT -> 1080 to 1920
            ImageUseCase.THUMBNAIL -> 256 to 256
        }
    }
    
    enum class ImageUseCase {
        PROFILE_PHOTO,
        VEHICLE_DOCUMENT,
        RECEIPT,
        THUMBNAIL
    }
}
