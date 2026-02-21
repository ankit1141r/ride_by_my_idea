package com.rideconnect.core.common.ui

import androidx.compose.foundation.layout.*
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Error
import androidx.compose.material.icons.filled.Refresh
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import com.rideconnect.core.common.accessibility.AccessibilityUtils
import com.rideconnect.core.common.accessibility.accessibleTouchTarget
import com.rideconnect.core.common.error.ErrorHandler

/**
 * Error dialog with retry option
 * Requirements: 26.1, 26.4, 26.5
 */
@Composable
fun ErrorDialog(
    error: Throwable,
    onDismiss: () -> Unit,
    onRetry: (() -> Unit)? = null
) {
    val context = LocalContext.current
    val errorMessage = ErrorHandler.getErrorMessage(context, error)
    val suggestedAction = ErrorHandler.getSuggestedAction(context, error)
    val isRetryable = ErrorHandler.isRetryable(error)
    
    AlertDialog(
        onDismissRequest = onDismiss,
        icon = {
            Icon(
                imageVector = Icons.Default.Error,
                contentDescription = "Error icon",
                tint = MaterialTheme.colorScheme.error
            )
        },
        title = {
            Text(
                text = "Error",
                style = MaterialTheme.typography.headlineSmall
            )
        },
        text = {
            Column(verticalArrangement = Arrangement.spacedBy(8.dp)) {
                Text(errorMessage)
                suggestedAction?.let { action ->
                    Spacer(modifier = Modifier.height(8.dp))
                    Text(
                        text = action,
                        style = MaterialTheme.typography.bodyMedium,
                        color = MaterialTheme.colorScheme.onSurfaceVariant
                    )
                }
            }
        },
        confirmButton = {
            if (isRetryable && onRetry != null) {
                Button(
                    onClick = {
                        AccessibilityUtils.provideHapticFeedback(context)
                        onDismiss()
                        onRetry()
                    },
                    modifier = Modifier.accessibleTouchTarget()
                ) {
                    Icon(
                        imageVector = Icons.Default.Refresh,
                        contentDescription = null,
                        modifier = Modifier.size(18.dp)
                    )
                    Spacer(modifier = Modifier.width(4.dp))
                    Text("Retry")
                }
            } else {
                TextButton(
                    onClick = onDismiss,
                    modifier = Modifier.accessibleTouchTarget()
                ) {
                    Text("OK")
                }
            }
        },
        dismissButton = if (isRetryable && onRetry != null) {
            {
                TextButton(
                    onClick = onDismiss,
                    modifier = Modifier.accessibleTouchTarget()
                ) {
                    Text("Dismiss")
                }
            }
        } else null
    )
}

/**
 * Error snackbar with retry action
 * Requirements: 26.1, 26.5
 */
@Composable
fun ErrorSnackbar(
    snackbarHostState: SnackbarHostState,
    error: Throwable,
    onRetry: (() -> Unit)? = null
) {
    val context = LocalContext.current
    val errorMessage = ErrorHandler.getErrorMessage(context, error)
    val isRetryable = ErrorHandler.isRetryable(error)
    
    SnackbarHost(hostState = snackbarHostState) { data ->
        Snackbar(
            action = if (isRetryable && onRetry != null) {
                {
                    TextButton(
                        onClick = {
                            AccessibilityUtils.provideHapticFeedback(context)
                            onRetry()
                        }
                    ) {
                        Text("Retry")
                    }
                }
            } else null,
            modifier = Modifier.padding(16.dp)
        ) {
            Text(errorMessage)
        }
    }
}

/**
 * Full-screen error state with retry button
 * Requirements: 26.1, 26.5
 */
@Composable
fun ErrorState(
    error: Throwable,
    onRetry: () -> Unit,
    modifier: Modifier = Modifier
) {
    val context = LocalContext.current
    val errorMessage = ErrorHandler.getErrorMessage(context, error)
    val suggestedAction = ErrorHandler.getSuggestedAction(context, error)
    
    Column(
        modifier = modifier
            .fillMaxSize()
            .padding(32.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        Icon(
            imageVector = Icons.Default.Error,
            contentDescription = "Error icon",
            tint = MaterialTheme.colorScheme.error,
            modifier = Modifier.size(64.dp)
        )
        
        Spacer(modifier = Modifier.height(16.dp))
        
        Text(
            text = errorMessage,
            style = MaterialTheme.typography.titleMedium,
            textAlign = TextAlign.Center
        )
        
        suggestedAction?.let { action ->
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = action,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                textAlign = TextAlign.Center
            )
        }
        
        Spacer(modifier = Modifier.height(24.dp))
        
        Button(
            onClick = {
                AccessibilityUtils.provideHapticFeedback(context)
                onRetry()
            },
            modifier = Modifier.accessibleTouchTarget()
        ) {
            Icon(
                imageVector = Icons.Default.Refresh,
                contentDescription = null,
                modifier = Modifier.size(18.dp)
            )
            Spacer(modifier = Modifier.width(8.dp))
            Text("Retry")
        }
    }
}

/**
 * Inline error message with retry button
 * Requirements: 26.1, 26.5
 */
@Composable
fun InlineError(
    error: Throwable,
    onRetry: () -> Unit,
    modifier: Modifier = Modifier
) {
    val context = LocalContext.current
    val errorMessage = ErrorHandler.getErrorMessage(context, error)
    
    Card(
        modifier = modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.errorContainer
        )
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Row(
                modifier = Modifier.weight(1f),
                horizontalArrangement = Arrangement.spacedBy(12.dp),
                verticalAlignment = Alignment.CenterVertically
            ) {
                Icon(
                    imageVector = Icons.Default.Error,
                    contentDescription = "Error icon",
                    tint = MaterialTheme.colorScheme.onErrorContainer
                )
                Text(
                    text = errorMessage,
                    style = MaterialTheme.typography.bodyMedium,
                    color = MaterialTheme.colorScheme.onErrorContainer
                )
            }
            
            TextButton(
                onClick = {
                    AccessibilityUtils.provideHapticFeedback(context)
                    onRetry()
                },
                modifier = Modifier.accessibleTouchTarget()
            ) {
                Text(
                    text = "Retry",
                    color = MaterialTheme.colorScheme.onErrorContainer
                )
            }
        }
    }
}

/**
 * Loading indicator with message
 * Requirements: 26.5
 */
@Composable
fun LoadingIndicator(
    message: String? = null,
    modifier: Modifier = Modifier
) {
    val loadingMessage = message ?: "Loading..."
    
    Column(
        modifier = modifier
            .fillMaxWidth()
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        CircularProgressIndicator()
        Text(
            text = loadingMessage,
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant
        )
    }
}

/**
 * Full-screen loading state
 * Requirements: 26.5
 */
@Composable
fun LoadingState(
    message: String? = null,
    modifier: Modifier = Modifier
) {
    val loadingMessage = message ?: "Loading..."
    
    Box(
        modifier = modifier.fillMaxSize(),
        contentAlignment = Alignment.Center
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            CircularProgressIndicator(
                modifier = Modifier.size(48.dp)
            )
            Text(
                text = loadingMessage,
                style = MaterialTheme.typography.bodyLarge,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}

/**
 * Success feedback with message
 * Requirements: 26.6
 */
@Composable
fun SuccessMessage(
    message: String,
    onDismiss: () -> Unit,
    modifier: Modifier = Modifier
) {
    Snackbar(
        modifier = modifier.padding(16.dp),
        action = {
            TextButton(onClick = onDismiss) {
                Text("OK")
            }
        }
    ) {
        Text(message)
    }
}
