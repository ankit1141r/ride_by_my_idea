package com.rideconnect.core.common.ui

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Star
import androidx.compose.material.icons.filled.StarBorder
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.window.Dialog

/**
 * Rating dialog for submitting ratings and reviews.
 * Requirements: 8.1, 8.2, 8.4
 */
@Composable
fun RatingDialog(
    rideId: String,
    driverName: String,
    onSubmit: (Int, String?) -> Unit,
    onDismiss: () -> Unit,
    modifier: Modifier = Modifier
) {
    var selectedRating by remember { mutableStateOf(0) }
    var reviewText by remember { mutableStateOf("") }
    var showError by remember { mutableStateOf(false) }
    
    Dialog(onDismissRequest = onDismiss) {
        Card(
            modifier = modifier.fillMaxWidth(),
            shape = MaterialTheme.shapes.large
        ) {
            Column(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(24.dp),
                horizontalAlignment = Alignment.CenterHorizontally,
                verticalArrangement = Arrangement.spacedBy(16.dp)
            ) {
                // Title
                Text(
                    text = "Rate Your Ride",
                    style = MaterialTheme.typography.headlineSmall,
                    fontWeight = FontWeight.Bold
                )
                
                Text(
                    text = "How was your experience with $driverName?",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                
                // Star Rating
                Row(
                    horizontalArrangement = Arrangement.spacedBy(8.dp),
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    for (i in 1..5) {
                        Icon(
                            imageVector = if (i <= selectedRating) Icons.Default.Star else Icons.Default.StarBorder,
                            contentDescription = "$i stars",
                            tint = if (i <= selectedRating) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.onSurfaceVariant,
                            modifier = Modifier
                                .size(48.dp)
                                .clickable { selectedRating = i }
                        )
                    }
                }
                
                // Error message
                if (showError) {
                    Text(
                        text = "Please select a rating",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.error
                    )
                }
                
                // Review Text Field
                OutlinedTextField(
                    value = reviewText,
                    onValueChange = { 
                        if (it.length <= 500) {
                            reviewText = it
                        }
                    },
                    label = { Text("Add a review (optional)") },
                    placeholder = { Text("Share your experience...") },
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(120.dp),
                    maxLines = 4,
                    supportingText = {
                        Text(
                            text = "${reviewText.length}/500",
                            style = MaterialTheme.typography.bodySmall
                        )
                    }
                )
                
                // Buttons
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    OutlinedButton(
                        onClick = onDismiss,
                        modifier = Modifier.weight(1f)
                    ) {
                        Text("Cancel")
                    }
                    
                    Button(
                        onClick = {
                            if (selectedRating > 0) {
                                onSubmit(
                                    selectedRating,
                                    reviewText.takeIf { it.isNotBlank() }
                                )
                            } else {
                                showError = true
                            }
                        },
                        modifier = Modifier.weight(1f)
                    ) {
                        Text("Submit")
                    }
                }
            }
        }
    }
}

/**
 * Star rating display component.
 * Requirements: 8.4, 8.5
 */
@Composable
fun StarRatingDisplay(
    rating: Double,
    modifier: Modifier = Modifier,
    showValue: Boolean = true
) {
    Row(
        modifier = modifier,
        horizontalArrangement = Arrangement.spacedBy(4.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        for (i in 1..5) {
            Icon(
                imageVector = if (i <= rating) Icons.Default.Star else Icons.Default.StarBorder,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.primary,
                modifier = Modifier.size(20.dp)
            )
        }
        
        if (showValue) {
            Spacer(modifier = Modifier.width(4.dp))
            Text(
                text = String.format("%.1f", rating),
                style = MaterialTheme.typography.bodyMedium,
                fontWeight = FontWeight.Medium
            )
        }
    }
}
