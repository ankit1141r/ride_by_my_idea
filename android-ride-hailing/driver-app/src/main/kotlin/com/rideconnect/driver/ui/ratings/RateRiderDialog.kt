package com.rideconnect.driver.ui.ratings

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
 * Dialog for drivers to rate riders after ride completion.
 * Requirements: 16.4
 */
@Composable
fun RateRiderDialog(
    rideId: String,
    riderName: String,
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
                    text = "Rate Rider",
                    style = MaterialTheme.typography.headlineSmall,
                    fontWeight = FontWeight.Bold
                )
                
                Text(
                    text = "How was your experience with $riderName?",
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
                
                // Review Text Field (Optional)
                OutlinedTextField(
                    value = reviewText,
                    onValueChange = { 
                        if (it.length <= 500) {
                            reviewText = it
                        }
                    },
                    label = { Text("Add a comment (optional)") },
                    placeholder = { Text("Share your feedback...") },
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(100.dp),
                    maxLines = 3,
                    supportingText = {
                        Text(
                            text = "${reviewText.length}/500",
                            style = MaterialTheme.typography.bodySmall
                        )
                    }
                )
                
                // Quick Rating Options
                Text(
                    text = "Quick feedback:",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    modifier = Modifier.fillMaxWidth()
                )
                
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    QuickFeedbackChip(
                        text = "Polite",
                        onClick = { reviewText = "Polite and respectful" }
                    )
                    QuickFeedbackChip(
                        text = "On time",
                        onClick = { reviewText = "Was ready on time" }
                    )
                    QuickFeedbackChip(
                        text = "Friendly",
                        onClick = { reviewText = "Friendly and pleasant" }
                    )
                }
                
                // Buttons
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(8.dp)
                ) {
                    OutlinedButton(
                        onClick = onDismiss,
                        modifier = Modifier.weight(1f)
                    ) {
                        Text("Skip")
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

@Composable
private fun QuickFeedbackChip(
    text: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    SuggestionChip(
        onClick = onClick,
        label = { Text(text) },
        modifier = modifier
    )
}
