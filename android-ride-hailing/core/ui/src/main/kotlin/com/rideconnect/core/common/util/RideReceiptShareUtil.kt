package com.rideconnect.core.common.util

import android.content.Context
import android.content.Intent
import android.graphics.Bitmap
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.graphics.pdf.PdfDocument
import androidx.core.content.FileProvider
import com.rideconnect.core.domain.model.Ride
import java.io.File
import java.io.FileOutputStream
import java.text.SimpleDateFormat
import java.util.*

/**
 * Utility for generating and sharing ride receipts
 */
object RideReceiptShareUtil {
    
    /**
     * Share ride receipt as PDF
     */
    fun shareReceiptAsPdf(
        context: Context,
        ride: Ride,
        driverName: String? = null
    ) {
        try {
            val pdfFile = generatePdfReceipt(context, ride, driverName)
            shareFile(context, pdfFile, "application/pdf", "Share Receipt")
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }
    
    /**
     * Share ride receipt as image
     */
    fun shareReceiptAsImage(
        context: Context,
        ride: Ride,
        driverName: String? = null
    ) {
        try {
            val imageFile = generateImageReceipt(context, ride, driverName)
            shareFile(context, imageFile, "image/png", "Share Receipt")
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }
    
    /**
     * Generate PDF receipt
     */
    private fun generatePdfReceipt(
        context: Context,
        ride: Ride,
        driverName: String?
    ): File {
        val pdfDocument = PdfDocument()
        val pageInfo = PdfDocument.PageInfo.Builder(595, 842, 1).create() // A4 size
        val page = pdfDocument.startPage(pageInfo)
        
        val canvas = page.canvas
        val paint = Paint()
        paint.isAntiAlias = true
        
        var yPosition = 50f
        
        // Title
        paint.textSize = 28f
        paint.isFakeBoldText = true
        paint.color = Color.BLACK
        canvas.drawText("Ride Receipt", 50f, yPosition, paint)
        yPosition += 50f
        
        // Date
        paint.textSize = 14f
        paint.isFakeBoldText = false
        val dateFormatter = SimpleDateFormat("MMMM dd, yyyy • hh:mm a", Locale.getDefault())
        val dateStr = ride.completedAt?.let { dateFormatter.format(Date(it)) }
            ?: dateFormatter.format(Date(ride.requestedAt))
        canvas.drawText(dateStr, 50f, yPosition, paint)
        yPosition += 40f
        
        // Ride ID
        paint.textSize = 12f
        canvas.drawText("Ride ID: ${ride.id.take(8).uppercase()}", 50f, yPosition, paint)
        yPosition += 40f
        
        // Ride Details Section
        paint.textSize = 18f
        paint.isFakeBoldText = true
        canvas.drawText("Ride Details", 50f, yPosition, paint)
        yPosition += 30f
        
        paint.textSize = 14f
        paint.isFakeBoldText = false
        
        // Pickup
        canvas.drawText("Pickup:", 50f, yPosition, paint)
        yPosition += 20f
        canvas.drawText(ride.pickupLocation.address ?: "Pickup location", 70f, yPosition, paint)
        yPosition += 30f
        
        // Dropoff
        canvas.drawText("Dropoff:", 50f, yPosition, paint)
        yPosition += 20f
        canvas.drawText(ride.dropoffLocation.address ?: "Dropoff location", 70f, yPosition, paint)
        yPosition += 30f
        
        // Distance and Duration
        ride.distance?.let { distance ->
            canvas.drawText("Distance: ${"%.1f km".format(distance)}", 50f, yPosition, paint)
            yPosition += 25f
        }
        
        ride.duration?.let { duration ->
            canvas.drawText("Duration: $duration minutes", 50f, yPosition, paint)
            yPosition += 25f
        }
        
        yPosition += 20f
        
        // Driver Details
        driverName?.let { name ->
            paint.textSize = 18f
            paint.isFakeBoldText = true
            canvas.drawText("Driver Details", 50f, yPosition, paint)
            yPosition += 30f
            
            paint.textSize = 14f
            paint.isFakeBoldText = false
            canvas.drawText("Driver: $name", 50f, yPosition, paint)
            yPosition += 40f
        }
        
        // Fare Breakdown
        ride.fare?.let { fare ->
            paint.textSize = 18f
            paint.isFakeBoldText = true
            canvas.drawText("Fare Breakdown", 50f, yPosition, paint)
            yPosition += 30f
            
            paint.textSize = 14f
            paint.isFakeBoldText = false
            
            val baseFare = fare * 0.4
            val distanceCharge = fare * 0.4
            val timeCharge = fare * 0.2
            
            canvas.drawText("Base Fare: ₹${"%.2f".format(baseFare)}", 50f, yPosition, paint)
            yPosition += 25f
            canvas.drawText("Distance Charge: ₹${"%.2f".format(distanceCharge)}", 50f, yPosition, paint)
            yPosition += 25f
            canvas.drawText("Time Charge: ₹${"%.2f".format(timeCharge)}", 50f, yPosition, paint)
            yPosition += 35f
            
            // Total
            paint.textSize = 20f
            paint.isFakeBoldText = true
            canvas.drawText("Total: ₹${"%.2f".format(fare)}", 50f, yPosition, paint)
        }
        
        pdfDocument.finishPage(page)
        
        // Save PDF
        val file = File(context.cacheDir, "ride_receipt_${ride.id.take(8)}.pdf")
        pdfDocument.writeTo(FileOutputStream(file))
        pdfDocument.close()
        
        return file
    }
    
    /**
     * Generate image receipt
     */
    private fun generateImageReceipt(
        context: Context,
        ride: Ride,
        driverName: String?
    ): File {
        val width = 800
        val height = 1400
        val bitmap = Bitmap.createBitmap(width, height, Bitmap.Config.ARGB_8888)
        val canvas = Canvas(bitmap)
        
        // White background
        canvas.drawColor(Color.WHITE)
        
        val paint = Paint()
        paint.color = Color.BLACK
        paint.isAntiAlias = true
        
        var yPosition = 60f
        
        // Title
        paint.textSize = 36f
        paint.isFakeBoldText = true
        canvas.drawText("Ride Receipt", 50f, yPosition, paint)
        yPosition += 60f
        
        // Date
        paint.textSize = 20f
        paint.isFakeBoldText = false
        val dateFormatter = SimpleDateFormat("MMMM dd, yyyy • hh:mm a", Locale.getDefault())
        val dateStr = ride.completedAt?.let { dateFormatter.format(Date(it)) }
            ?: dateFormatter.format(Date(ride.requestedAt))
        canvas.drawText(dateStr, 50f, yPosition, paint)
        yPosition += 50f
        
        // Ride ID
        paint.textSize = 16f
        canvas.drawText("Ride ID: ${ride.id.take(8).uppercase()}", 50f, yPosition, paint)
        yPosition += 60f
        
        // Ride Details Section
        paint.textSize = 26f
        paint.isFakeBoldText = true
        canvas.drawText("Ride Details", 50f, yPosition, paint)
        yPosition += 45f
        
        paint.textSize = 20f
        paint.isFakeBoldText = false
        
        // Pickup
        canvas.drawText("Pickup:", 50f, yPosition, paint)
        yPosition += 30f
        canvas.drawText(ride.pickupLocation.address ?: "Pickup location", 80f, yPosition, paint)
        yPosition += 45f
        
        // Dropoff
        canvas.drawText("Dropoff:", 50f, yPosition, paint)
        yPosition += 30f
        canvas.drawText(ride.dropoffLocation.address ?: "Dropoff location", 80f, yPosition, paint)
        yPosition += 45f
        
        // Distance and Duration
        ride.distance?.let { distance ->
            canvas.drawText("Distance: ${"%.1f km".format(distance)}", 50f, yPosition, paint)
            yPosition += 35f
        }
        
        ride.duration?.let { duration ->
            canvas.drawText("Duration: $duration minutes", 50f, yPosition, paint)
            yPosition += 35f
        }
        
        yPosition += 30f
        
        // Driver Details
        driverName?.let { name ->
            paint.textSize = 26f
            paint.isFakeBoldText = true
            canvas.drawText("Driver Details", 50f, yPosition, paint)
            yPosition += 45f
            
            paint.textSize = 20f
            paint.isFakeBoldText = false
            canvas.drawText("Driver: $name", 50f, yPosition, paint)
            yPosition += 60f
        }
        
        // Fare Breakdown
        ride.fare?.let { fare ->
            paint.textSize = 26f
            paint.isFakeBoldText = true
            canvas.drawText("Fare Breakdown", 50f, yPosition, paint)
            yPosition += 45f
            
            paint.textSize = 20f
            paint.isFakeBoldText = false
            
            val baseFare = fare * 0.4
            val distanceCharge = fare * 0.4
            val timeCharge = fare * 0.2
            
            canvas.drawText("Base Fare: ₹${"%.2f".format(baseFare)}", 50f, yPosition, paint)
            yPosition += 35f
            canvas.drawText("Distance Charge: ₹${"%.2f".format(distanceCharge)}", 50f, yPosition, paint)
            yPosition += 35f
            canvas.drawText("Time Charge: ₹${"%.2f".format(timeCharge)}", 50f, yPosition, paint)
            yPosition += 50f
            
            // Total
            paint.textSize = 28f
            paint.isFakeBoldText = true
            canvas.drawText("Total: ₹${"%.2f".format(fare)}", 50f, yPosition, paint)
        }
        
        // Save image
        val file = File(context.cacheDir, "ride_receipt_${ride.id.take(8)}.png")
        FileOutputStream(file).use { out ->
            bitmap.compress(Bitmap.CompressFormat.PNG, 100, out)
        }
        
        return file
    }
    
    /**
     * Share file using Android share intent
     */
    private fun shareFile(
        context: Context,
        file: File,
        mimeType: String,
        title: String
    ) {
        val uri = FileProvider.getUriForFile(
            context,
            "${context.packageName}.fileprovider",
            file
        )
        
        val shareIntent = Intent(Intent.ACTION_SEND).apply {
            type = mimeType
            putExtra(Intent.EXTRA_STREAM, uri)
            addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION)
        }
        
        context.startActivity(Intent.createChooser(shareIntent, title))
    }
}
