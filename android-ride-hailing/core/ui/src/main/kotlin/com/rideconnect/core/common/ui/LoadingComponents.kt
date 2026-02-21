package com.rideconnect.core.common.ui

import androidx.compose.animation.core.*
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Brush
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.unit.dp
import com.rideconnect.core.common.theme.Dimensions

/**
 * Standardized loading components with consistent styling and animations.
 */

/**
 * Full-screen loading indicator with optional message.
 */
@Composable
fun FullScreenLoading(
    message: String = "Loading...",
    modifier: Modifier = Modifier
) {
    Box(
        modifier = modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
            .semantics {
                contentDescription = message
            },
        contentAlignment = Alignment.Center
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(Dimensions.spaceMedium)
        ) {
            CircularProgressIndicator(
                modifier = Modifier.size(Dimensions.progressIndicatorSize),
                color = MaterialTheme.colorScheme.primary,
                strokeWidth = Dimensions.progressIndicatorStrokeWidth
            )
            
            Text(
                text = message,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onBackground
            )
        }
    }
}

/**
 * Inline loading indicator for use within content.
 */
@Composable
fun InlineLoading(
    message: String = "Loading...",
    modifier: Modifier = Modifier
) {
    Row(
        modifier = modifier
            .fillMaxWidth()
            .padding(Dimensions.paddingMedium)
            .semantics {
                contentDescription = message
            },
        horizontalArrangement = Arrangement.Center,
        verticalAlignment = Alignment.CenterVertically
    ) {
        CircularProgressIndicator(
            modifier = Modifier.size(Dimensions.progressIndicatorSizeSmall),
            color = MaterialTheme.colorScheme.primary,
            strokeWidth = 2.dp
        )
        
        Spacer(modifier = Modifier.width(Dimensions.spaceSmall))
        
        Text(
            text = message,
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurface
        )
    }
}

/**
 * Skeleton loading placeholder for content.
 * Creates a shimmer effect while content is loading.
 */
@Composable
fun SkeletonBox(
    modifier: Modifier = Modifier,
    shape: RoundedCornerShape = RoundedCornerShape(Dimensions.cornerRadiusMedium)
) {
    val infiniteTransition = rememberInfiniteTransition(label = "skeleton")
    val shimmerTranslate by infiniteTransition.animateFloat(
        initialValue = 0f,
        targetValue = 1000f,
        animationSpec = infiniteRepeatable(
            animation = tween(
                durationMillis = 1200,
                easing = LinearEasing
            ),
            repeatMode = RepeatMode.Restart
        ),
        label = "shimmer"
    )
    
    val shimmerColors = listOf(
        MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.3f),
        MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.5f),
        MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.3f)
    )
    
    Box(
        modifier = modifier
            .clip(shape)
            .background(
                brush = Brush.horizontalGradient(
                    colors = shimmerColors,
                    startX = shimmerTranslate - 1000f,
                    endX = shimmerTranslate
                )
            )
    )
}

/**
 * Skeleton loading for a list item.
 */
@Composable
fun SkeletonListItem(
    modifier: Modifier = Modifier
) {
    Row(
        modifier = modifier
            .fillMaxWidth()
            .padding(Dimensions.paddingMedium),
        horizontalArrangement = Arrangement.spacedBy(Dimensions.spaceMedium)
    ) {
        // Avatar placeholder
        SkeletonBox(
            modifier = Modifier.size(48.dp),
            shape = RoundedCornerShape(Dimensions.cornerRadiusFull)
        )
        
        Column(
            modifier = Modifier.weight(1f),
            verticalArrangement = Arrangement.spacedBy(Dimensions.spaceSmall)
        ) {
            // Title placeholder
            SkeletonBox(
                modifier = Modifier
                    .fillMaxWidth(0.7f)
                    .height(16.dp)
            )
            
            // Subtitle placeholder
            SkeletonBox(
                modifier = Modifier
                    .fillMaxWidth(0.5f)
                    .height(14.dp)
            )
        }
    }
}

/**
 * Skeleton loading for a card.
 */
@Composable
fun SkeletonCard(
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier
            .fillMaxWidth()
            .padding(Dimensions.paddingMedium),
        verticalArrangement = Arrangement.spacedBy(Dimensions.spaceSmall)
    ) {
        // Image placeholder
        SkeletonBox(
            modifier = Modifier
                .fillMaxWidth()
                .height(200.dp)
        )
        
        // Title placeholder
        SkeletonBox(
            modifier = Modifier
                .fillMaxWidth(0.8f)
                .height(20.dp)
        )
        
        // Content placeholders
        repeat(3) {
            SkeletonBox(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(14.dp)
            )
        }
    }
}

/**
 * Loading overlay that can be placed over existing content.
 */
@Composable
fun LoadingOverlay(
    isLoading: Boolean,
    message: String = "Loading...",
    modifier: Modifier = Modifier,
    content: @Composable () -> Unit
) {
    Box(modifier = modifier) {
        content()
        
        if (isLoading) {
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .background(Color.Black.copy(alpha = 0.5f))
                    .semantics {
                        contentDescription = message
                    },
                contentAlignment = Alignment.Center
            ) {
                Column(
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.spacedBy(Dimensions.spaceMedium)
                ) {
                    CircularProgressIndicator(
                        modifier = Modifier.size(Dimensions.progressIndicatorSize),
                        color = Color.White,
                        strokeWidth = Dimensions.progressIndicatorStrokeWidth
                    )
                    
                    Text(
                        text = message,
                        style = MaterialTheme.typography.bodyMedium,
                        color = Color.White
                    )
                }
            }
        }
    }
}

/**
 * Small loading indicator for buttons.
 */
@Composable
fun ButtonLoading(
    modifier: Modifier = Modifier
) {
    CircularProgressIndicator(
        modifier = modifier.size(20.dp),
        color = MaterialTheme.colorScheme.onPrimary,
        strokeWidth = 2.dp
    )
}

/**
 * Pulsing dot loading indicator.
 */
@Composable
fun PulsingDots(
    modifier: Modifier = Modifier,
    dotCount: Int = 3
) {
    Row(
        modifier = modifier,
        horizontalArrangement = Arrangement.spacedBy(Dimensions.spaceSmall)
    ) {
        repeat(dotCount) { index ->
            val infiniteTransition = rememberInfiniteTransition(label = "dot$index")
            val scale by infiniteTransition.animateFloat(
                initialValue = 0.5f,
                targetValue = 1f,
                animationSpec = infiniteRepeatable(
                    animation = tween(
                        durationMillis = 600,
                        delayMillis = index * 200,
                        easing = FastOutSlowInEasing
                    ),
                    repeatMode = RepeatMode.Reverse
                ),
                label = "scale$index"
            )
            
            Box(
                modifier = Modifier
                    .size((8 * scale).dp)
                    .clip(RoundedCornerShape(Dimensions.cornerRadiusFull))
                    .background(MaterialTheme.colorScheme.primary)
            )
        }
    }
}
