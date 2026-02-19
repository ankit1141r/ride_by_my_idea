package com.rideconnect.core.common.util

import android.content.Context
import android.content.Intent
import android.graphics.Bitmap
import android.graphics.Canvas
import android.graphics.Color
import android.graphics.Paint
import android.graphics.pdf.PdfDocument
import androidx.core.content.FileProvider
import com.rideconnect.core.domain.model.Receipt
import java.io.File
import java.io.FileOutputStream
import java.text.SimpleDateFormat
import java.util.*

/**
 * Utility for generating and sharing receipts.
 * Requirements: 7.3, 7.6, 7.7, 28.6
 */
object ReceiptShareUtil {
    
    /**
     * Generate receipt as PDF and share.
     * Requirements: 7.6, 7.7, 28.6
     */
    fun shareReceiptAsPdf(context: Context, receipt: Receipt) {
        try {
            val pdfFile = generatePdfReceipt(context, receipt)
            shareFile(context, pdfFile, "application/pdf")
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }
    
    /**
     * Generate receipt as image and share.
     * Requirements: 7.6, 7.7, 28.6
     */
    fun shareReceiptAsImage(context: Context, receipt: Receipt) {
        try {
            val imageFile = generateImageReceipt(context, receipt)
            shareFile(context, imageFile, "image/png")
        } catch (e: Exception) {
            e.printStackTrace()
        }
    }
    
    /**
     * Generate PDF receipt.
     */
    private fun generatePdfReceipt(context: Context, receipt: Receipt): File {
        val pdfDocument = PdfDocument()
        val pageInfo = PdfDocument.PageInfo.Builder(595, 842, 1).create() // A4 size
        val page = pdfDocument.startPage(pageInfo)
        
        val canvas = page.canvas
        val paint = Paint()
        
        // Draw receipt content
        var yPosition = 50f
        
        // Title
        paint.textSize = 24f
        paint.isFakeBoldText = true
        canvas.drawText("Payment Receipt", 50f, yPosition, paint)
        yPosition += 40f
        
        // Date
        paint.textSize = 14f
        paint.isFakeBoldText = false
        canvas.drawText(formatDate(receipt.transaction.createdAt), 50f, yPosition, paint)
        yPosition += 40f
        
        // Transaction Details
        paint.textSize = 18f
        paint.isFakeBoldText = true
        canvas.drawText("Transaction Details", 50f, yPosition, paint)
        yPosition += 30f
        
        paint.textSize = 14f
        paint.isFakeBoldText = false
        canvas.drawText("Transaction ID: ${receipt.transaction.transactionId ?: "N/A"}", 50f, yPosition, paint)
        yPosition += 25f
        canvas.drawText("Ride ID: ${receipt.transaction.rideId}", 50f, yPosition, paint)
        yPosition += 25f
        canvas.drawText("Payment Method: ${receipt.transaction.paymentMethod.name}", 50f, yPosition, paint)
        yPosition += 25f
        canvas.drawText("Status: ${receipt.transaction.status.name}", 50f, yPosition, paint)
        yPosition += 40f
        
        // Ride Details
        paint.textSize = 18f
        paint.isFakeBoldText = true
        canvas.drawText("Ride Details", 50f, yPosition, paint)
        yPosition += 30f
        
        paint.textSize = 14f
        paint.isFakeBoldText = false
        canvas.drawText("Pickup: ${receipt.ride.pickupLocation.address ?: "Unknown"}", 50f, yPosition, paint)
        yPosition += 25f
        canvas.drawText("Dropoff: ${receipt.ride.dropoffLocation.address ?: "Unknown"}", 50f, yPosition, paint)
        yPosition += 25f
        receipt.ride.distance?.let {
            canvas.drawText("Distance: ${String.format("%.2f", it)} km", 50f, yPosition, paint)
            yPosition += 25f
        }
        receipt.ride.duration?.let {
            canvas.drawText("Duration: $it minutes", 50f, yPosition, paint)
            yPosition += 25f
        }
        yPosition += 15f
        
        // Fare Breakdown
        paint.textSize = 18f
        paint.isFakeBoldText = true
        canvas.drawText("Fare Breakdown", 50f, yPosition, paint)
        yPosition += 30f
        
        paint.textSize = 14f
        paint.isFakeBoldText = false
        canvas.drawText("Base Fare: ₹${String.format("%.2f", receipt.fareBreakdown.baseFare)}", 50f, yPosition, paint)
        yPosition += 25f
        canvas.drawText("Distance Fare: ₹${String.format("%.2f", receipt.fareBreakdown.distanceFare)}", 50f, yPosition, paint)
        yPosition += 25f
        canvas.drawText("Time Fare: ₹${String.format("%.2f", receipt.fareBreakdown.timeFare)}", 50f, yPosition, paint)
        yPosition += 35f
        
        // Total
        paint.textSize = 18f
        paint.isFakeBoldText = true
        canvas.drawText("Total Amount: ₹${String.format("%.2f", receipt.fareBreakdown.total)}", 50f, yPosition, paint)
        
        pdfDocument.finishPage(page)
        
        // Save PDF
        val file = File(context.cacheDir, "receipt_${receipt.transaction.id}.pdf")
        pdfDocument.writeTo(FileOutputStream(file))
        pdfDocument.close()
        
        return file
    }
    
    /**
     * Generate image receipt.
     */
    private fun generateImageReceipt(context: Context, receipt: Receipt): File {
        val width = 800
        val height = 1200
        val bitmap = Bitmap.createBitmap(width, height, Bitmap.Config.ARGB_8888)
        val canvas = Canvas(bitmap)
        
        // White background
        canvas.drawColor(Color.WHITE)
        
        val paint = Paint()
        paint.color = Color.BLACK
        paint.isAntiAlias = true
        
        var yPosition = 50f
        
        // Title
        paint.textSize = 32f
        paint.isFakeBoldText = true
        canvas.drawText("Payment Receipt", 50f, yPosition, paint)
        yPosition += 50f
        
        // Date
        paint.textSize = 18f
        paint.isFakeBoldText = false
        canvas.drawText(formatDate(receipt.transaction.createdAt), 50f, yPosition, paint)
        yPosition += 50f
        
        // Transaction Details
        paint.textSize = 24f
        paint.isFakeBoldText = true
        canvas.drawText("Transaction Details", 50f, yPosition, paint)
        yPosition += 40f
        
        paint.textSize = 18f
        paint.isFakeBoldText = false
        canvas.drawText("Transaction ID: ${receipt.transaction.transactionId ?: "N/A"}", 50f, yPosition, paint)
        yPosition += 30f
        canvas.drawText("Ride ID: ${receipt.transaction.rideId}", 50f, yPosition, paint)
        yPosition += 30f
        canvas.drawText("Payment Method: ${receipt.transaction.paymentMethod.name}", 50f, yPosition, paint)
        yPosition += 30f
        canvas.drawText("Status: ${receipt.transaction.status.name}", 50f, yPosition, paint)
        yPosition += 50f
        
        // Ride Details
        paint.textSize = 24f
        paint.isFakeBoldText = true
        canvas.drawText("Ride Details", 50f, yPosition, paint)
        yPosition += 40f
        
        paint.textSize = 18f
        paint.isFakeBoldText = false
        canvas.drawText("Pickup: ${receipt.ride.pickupLocation.address ?: "Unknown"}", 50f, yPosition, paint)
        yPosition += 30f
        canvas.drawText("Dropoff: ${receipt.ride.dropoffLocation.address ?: "Unknown"}", 50f, yPosition, paint)
        yPosition += 30f
        receipt.ride.distance?.let {
            canvas.drawText("Distance: ${String.format("%.2f", it)} km", 50f, yPosition, paint)
            yPosition += 30f
        }
        receipt.ride.duration?.let {
            canvas.drawText("Duration: $it minutes", 50f, yPosition, paint)
            yPosition += 30f
        }
        yPosition += 20f
        
        // Fare Breakdown
        paint.textSize = 24f
        paint.isFakeBoldText = true
        canvas.drawText("Fare Breakdown", 50f, yPosition, paint)
        yPosition += 40f
        
        paint.textSize = 18f
        paint.isFakeBoldText = false
        canvas.drawText("Base Fare: ₹${String.format("%.2f", receipt.fareBreakdown.baseFare)}", 50f, yPosition, paint)
        yPosition += 30f
        canvas.drawText("Distance Fare: ₹${String.format("%.2f", receipt.fareBreakdown.distanceFare)}", 50f, yPosition, paint)
        yPosition += 30f
        canvas.drawText("Time Fare: ₹${String.format("%.2f", receipt.fareBreakdown.timeFare)}", 50f, yPosition, paint)
        yPosition += 50f
        
        // Total
        paint.textSize = 24f
        paint.isFakeBoldText = true
        canvas.drawText("Total Amount: ₹${String.format("%.2f", receipt.fareBreakdown.total)}", 50f, yPosition, paint)
        
        // Save image
        val file = File(context.cacheDir, "receipt_${receipt.transaction.id}.png")
        FileOutputStream(file).use { out ->
            bitmap.compress(Bitmap.CompressFormat.PNG, 100, out)
        }
        
        return file
    }
    
    /**
     * Share file using Android share intent.
     */
    private fun shareFile(context: Context, file: File, mimeType: String) {
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
        
        context.startActivity(Intent.createChooser(shareIntent, "Share Receipt"))
    }
    
    private fun formatDate(timestamp: Long): String {
        val sdf = SimpleDateFormat("MMM dd, yyyy • hh:mm a", Locale.getDefault())
        return sdf.format(Date(timestamp))
    }
}
