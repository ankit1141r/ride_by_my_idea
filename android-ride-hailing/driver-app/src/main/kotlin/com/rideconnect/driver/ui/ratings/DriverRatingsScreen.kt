package com.rideconnect.driver.ui.ratings

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.TrendingDown
import androidx.compose.material.icons.filled.TrendingUp
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.rideconnect.core.common.ui.StarRatingDisplay
import com.rideconnect.core.domain.model.Rating
import com.rideconnect.core.domain.viewmodel.RatingUiState
import java.text.SimpleDateFormat
import java.util.*

/**
 * Driver ratings screen with performance metrics.
 * Requirements: 16.1, 16.2, 16.3, 16.5, 16.7
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun DriverRatingsScreen(
    uiState: RatingUiState,
    acceptanceRate: Double,
    cancellationRate: Double,
    completionRate: Double,
    onOpenDrawer: () -> Unit,
    modifier: Modifier = Modifier
) {
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Ratings & Performance") },
                navigationIcon = {
                    IconButton(onClick = onOpenDrawer) {
                        Icon(Icons.Default.Menu, contentDescription = "Open menu")
                    }
                }
            )
        }
    ) { paddingValues ->
        LazyColumn(
            modifier = modifier
                .fillMaxSize()
                .padding(paddingValues),
            contentPadding = PaddingValues(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Average Rating Card
            item {
                uiState.averageRating?.let { avgRating ->
                    DriverAverageRatingCard(
                        averageRating = avgRating.averageRating,
                        totalRatings = avgRating.totalRatings,
                        ratingBreakdown = avgRating.ratingBreakdown
                    )
                }
            }
            
            // Performance Metrics Card
            item {
                PerformanceMetricsCard(
                    acceptanceRate = acceptanceRate,
                    cancellationRate = cancellationRate,
                    completionRate = completionRate
                )
            }
            
            // Improvement Suggestions
            item {
                uiState.averageRating?.let { avgRating ->
                    if (avgRating.averageRating < 4.0) {
                        ImprovementSuggestionsCard(
                            averageRating = avgRating.averageRating
                        )
                    }
                }
            }
            
            // Recent Ratings Header
            item {
                Text(
                    text = "Recent Ratings",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold
                )
            }
            
            // Ratings List
            if (uiState.ratings.isEmpty()) {
                item {
                    EmptyRatingsState()
                }
            } else {
                items(uiState.ratings) { rating ->
                    DriverRatingCard(rating = rating)
                }
            }
        }
    }
}

@Composable
private fun DriverAverageRatingCard(
    averageRating: Double,
    totalRatings: Int,
    ratingBreakdown: com.rideconnect.core.domain.model.RatingBreakdown,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.primaryContainer
        )
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Text(
                text = "Your Rating",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                Column(
                    horizontalAlignment = Alignment.CenterHorizontally
                ) {
                    Text(
                        text = String.format("%.1f", averageRating),
                        style = MaterialTheme.typography.displayLarge,
                        fontWeight = FontWeight.Bold,
                        color = MaterialTheme.colorScheme.primary
                    )
                    StarRatingDisplay(
                        rating = averageRating,
                        showValue = false
                    )
                    Text(
                        text = "$totalRatings ratings",
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
                
                Column(
                    verticalArrangement = Arrangement.spacedBy(4.dp)
                ) {
                    RatingBreakdownRow(5, ratingBreakdown.fiveStars, totalRatings)
                    RatingBreakdownRow(4, ratingBreakdown.fourStars, totalRatings)
                    RatingBreakdownRow(3, ratingBreakdown.threeStars, totalRatings)
                    RatingBreakdownRow(2, ratingBreakdown.twoStars, totalRatings)
                    RatingBreakdownRow(1, ratingBreakdown.oneStar, totalRatings)
                }
            }
        }
    }
}

@Composable
private fun RatingBreakdownRow(
    stars: Int,
    count: Int,
    total: Int,
    modifier: Modifier = Modifier
) {
    Row(
        modifier = modifier.width(150.dp),
        horizontalArrangement = Arrangement.spacedBy(8.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(
            text = "$stars★",
            style = MaterialTheme.typography.bodySmall,
            modifier = Modifier.width(24.dp)
        )
        LinearProgressIndicator(
            progress = if (total > 0) count.toFloat() / total else 0f,
            modifier = Modifier
                .weight(1f)
                .height(8.dp)
        )
        Text(
            text = "$count",
            style = MaterialTheme.typography.bodySmall,
            modifier = Modifier.width(24.dp)
        )
    }
}

@Composable
private fun PerformanceMetricsCard(
    acceptanceRate: Double,
    cancellationRate: Double,
    completionRate: Double,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Text(
                text = "Performance Metrics",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
            
            PerformanceMetricRow(
                label = "Acceptance Rate",
                value = acceptanceRate,
                isGood = acceptanceRate >= 80.0
            )
            
            PerformanceMetricRow(
                label = "Cancellation Rate",
                value = cancellationRate,
                isGood = cancellationRate <= 5.0
            )
            
            PerformanceMetricRow(
                label = "Completion Rate",
                value = completionRate,
                isGood = completionRate >= 95.0
            )
        }
    }
}

@Composable
private fun PerformanceMetricRow(
    label: String,
    value: Double,
    isGood: Boolean,
    modifier: Modifier = Modifier
) {
    Row(
        modifier = modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween,
        verticalAlignment = Alignment.CenterVertically
    ) {
        Text(
            text = label,
            style = MaterialTheme.typography.bodyMedium
        )
        Row(
            horizontalArrangement = Arrangement.spacedBy(4.dp),
            verticalAlignment = Alignment.CenterVertically
        ) {
            Icon(
                imageVector = if (isGood) Icons.Default.TrendingUp else Icons.Default.TrendingDown,
                contentDescription = null,
                tint = if (isGood) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.error,
                modifier = Modifier.size(20.dp)
            )
            Text(
                text = "${String.format("%.1f", value)}%",
                style = MaterialTheme.typography.bodyMedium,
                fontWeight = FontWeight.Bold,
                color = if (isGood) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.error
            )
        }
    }
}

@Composable
private fun ImprovementSuggestionsCard(
    averageRating: Double,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.tertiaryContainer
        )
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Text(
                text = "Improvement Suggestions",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.onTertiaryContainer
            )
            
            Text(
                text = "Your rating is below 4.0. Here are some tips to improve:",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onTertiaryContainer
            )
            
            Column(
                verticalArrangement = Arrangement.spacedBy(4.dp)
            ) {
                SuggestionItem("• Be punctual and arrive on time")
                SuggestionItem("• Keep your vehicle clean and well-maintained")
                SuggestionItem("• Be polite and professional with riders")
                SuggestionItem("• Follow the best route and drive safely")
                SuggestionItem("• Communicate clearly with riders")
            }
        }
    }
}

@Composable
private fun SuggestionItem(
    text: String,
    modifier: Modifier = Modifier
) {
    Text(
        text = text,
        style = MaterialTheme.typography.bodySmall,
        color = MaterialTheme.colorScheme.onTertiaryContainer,
        modifier = modifier
    )
}

@Composable
private fun DriverRatingCard(
    rating: Rating,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                StarRatingDisplay(
                    rating = rating.rating.toDouble(),
                    showValue = false
                )
                Text(
                    text = formatDate(rating.createdAt),
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
            
            if (rating.review != null) {
                Text(
                    text = rating.review,
                    style = MaterialTheme.typography.bodyMedium
                )
            } else {
                Text(
                    text = "No review provided",
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
            }
        }
    }
}

@Composable
private fun EmptyRatingsState(
    modifier: Modifier = Modifier
) {
    Column(
        modifier = modifier
            .fillMaxWidth()
            .padding(32.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        Text(
            text = "No ratings yet",
            style = MaterialTheme.typography.titleMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
        Text(
            text = "Complete rides to receive ratings from riders",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
    }
}

private fun formatDate(timestamp: Long): String {
    val sdf = SimpleDateFormat("MMM dd, yyyy", Locale.getDefault())
    return sdf.format(Date(timestamp))
}
