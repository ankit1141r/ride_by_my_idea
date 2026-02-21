package com.rideconnect.core.common.ui

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.LocationOn
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalConfiguration
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.style.TextOverflow
import androidx.compose.ui.unit.dp
import com.rideconnect.core.common.util.AddressFormatter

/**
 * Composable for displaying location addresses with smart truncation
 * and accessibility support.
 * 
 * Handles long addresses gracefully at all text sizes while maintaining
 * full address availability through tap/long press.
 */
@Composable
fun LocationDisplay(
    address: String,
    modifier: Modifier = Modifier,
    label: String? = null,
    showIcon: Boolean = true,
    maxLines: Int = 2,
    onAddressTap: (() -> Unit)? = null
) {
    var showFullAddress by remember { mutableStateOf(false) }
    
    // Get current text size scale for smart truncation
    val configuration = LocalConfiguration.current
    val textSizeScale = configuration.fontScale
    
    // Determine if truncation is needed
    val needsTruncation = AddressFormatter.needsTruncation(address, textSizeScale)
    val displayAddress = if (needsTruncation && !showFullAddress) {
        AddressFormatter.formatAddress(address)
    } else {
        address
    }
    
    // Accessibility description
    val accessibilityAddress = AddressFormatter.formatForAccessibility(address)
    val contentDesc = if (label != null) {
        "$label: $accessibilityAddress"
    } else {
        accessibilityAddress
    }
    
    Card(
        modifier = modifier
            .fillMaxWidth()
            .then(
                if (needsTruncation || onAddressTap != null) {
                    Modifier.clickable {
                        if (needsTruncation) {
                            showFullAddress = !showFullAddress
                        }
                        onAddressTap?.invoke()
                    }
                } else {
                    Modifier
                }
            )
            .semantics {
                this.contentDescription = contentDesc
            },
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant
        )
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalArrangement = Arrangement.Start,
            verticalAlignment = Alignment.CenterVertically
        ) {
            if (showIcon) {
                Icon(
                    imageVector = Icons.Default.LocationOn,
                    contentDescription = null, // Decorative, address provides context
                    tint = MaterialTheme.colorScheme.primary,
                    modifier = Modifier.size(24.dp)
                )
                Spacer(modifier = Modifier.width(12.dp))
            }
            
            Column(
                modifier = Modifier.weight(1f)
            ) {
                if (label != null) {
                    Text(
                        text = label,
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                    Spacer(modifier = Modifier.height(4.dp))
                }
                
                Text(
                    text = displayAddress,
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    maxLines = if (showFullAddress) Int.MAX_VALUE else maxLines,
                    overflow = if (showFullAddress) TextOverflow.Visible else TextOverflow.Ellipsis
                )
                
                if (needsTruncation) {
                    Spacer(modifier = Modifier.height(4.dp))
                    Text(
                        text = if (showFullAddress) "Tap to collapse" else "Tap to see full address",
                        style = MaterialTheme.typography.labelSmall,
                        color = MaterialTheme.colorScheme.primary
                    )
                }
            }
        }
    }
}

/**
 * Compact location display for use in lists or tight spaces.
 */
@Composable
fun CompactLocationDisplay(
    address: String,
    modifier: Modifier = Modifier,
    icon: Boolean = true
) {
    Row(
        modifier = modifier,
        horizontalArrangement = Arrangement.Start,
        verticalAlignment = Alignment.CenterVertically
    ) {
        if (icon) {
            Icon(
                imageVector = Icons.Default.LocationOn,
                contentDescription = null,
                tint = MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier.size(16.dp)
            )
            Spacer(modifier = Modifier.width(4.dp))
        }
        
        Text(
            text = AddressFormatter.formatShortAddress(address),
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
            maxLines = 1,
            overflow = TextOverflow.Ellipsis,
            modifier = Modifier.semantics {
                contentDescription = AddressFormatter.formatForAccessibility(address)
            }
        )
    }
}

/**
 * Location pair display for showing pickup and dropoff together.
 */
@Composable
fun LocationPairDisplay(
    pickupAddress: String,
    dropoffAddress: String,
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier.fillMaxWidth(),
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        LocationDisplay(
            address = pickupAddress,
            label = "Pickup",
            showIcon = true
        )
        
        LocationDisplay(
            address = dropoffAddress,
            label = "Dropoff",
            showIcon = true
        )
    }
}
