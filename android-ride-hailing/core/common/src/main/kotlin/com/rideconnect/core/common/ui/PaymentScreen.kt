package com.rideconnect.core.common.ui

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ArrowBack
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Error
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import com.rideconnect.core.domain.model.FareBreakdown
import com.rideconnect.core.domain.model.PaymentMethod
import com.rideconnect.core.domain.viewmodel.PaymentUiState

/**
 * Payment screen for processing ride payments.
 * Requirements: 7.1, 7.2, 7.3, 7.4
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun PaymentScreen(
    rideId: String,
    fareBreakdown: FareBreakdown,
    uiState: PaymentUiState,
    onProcessPayment: (String, Double, PaymentMethod) -> Unit,
    onNavigateBack: () -> Unit,
    onViewReceipt: () -> Unit,
    modifier: Modifier = Modifier
) {
    var selectedPaymentMethod by remember { mutableStateOf(PaymentMethod.RAZORPAY) }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Payment") },
                navigationIcon = {
                    IconButton(onClick = onNavigateBack) {
                        Icon(Icons.Default.ArrowBack, contentDescription = "Back")
                    }
                }
            )
        }
    ) { paddingValues ->
        Column(
            modifier = modifier
                .fillMaxSize()
                .padding(paddingValues)
                .verticalScroll(rememberScrollState())
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            // Fare Breakdown Card
            FareBreakdownCard(fareBreakdown = fareBreakdown)
            
            // Payment Method Selection
            PaymentMethodSelector(
                selectedMethod = selectedPaymentMethod,
                onMethodSelected = { selectedPaymentMethod = it },
                enabled = !uiState.isProcessing
            )
            
            // Payment Status
            if (uiState.paymentSuccess) {
                PaymentSuccessCard(onViewReceipt = onViewReceipt)
            }
            
            // Error Message
            if (uiState.error != null) {
                PaymentErrorCard(error = uiState.error)
            }
            
            Spacer(modifier = Modifier.weight(1f))
            
            // Pay Button
            Button(
                onClick = {
                    onProcessPayment(rideId, fareBreakdown.total, selectedPaymentMethod)
                },
                modifier = Modifier.fillMaxWidth(),
                enabled = !uiState.isProcessing && !uiState.paymentSuccess
            ) {
                if (uiState.isProcessing) {
                    CircularProgressIndicator(
                        modifier = Modifier.size(24.dp),
                        color = MaterialTheme.colorScheme.onPrimary
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text("Processing...")
                } else {
                    Text("Pay ₹${String.format("%.2f", fareBreakdown.total)}")
                }
            }
        }
    }
}

@Composable
private fun FareBreakdownCard(
    fareBreakdown: FareBreakdown,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Text(
                text = "Fare Breakdown",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
            
            Divider(modifier = Modifier.padding(vertical = 8.dp))
            
            FareRow(label = "Base Fare", amount = fareBreakdown.baseFare)
            FareRow(label = "Distance Fare", amount = fareBreakdown.distanceFare)
            FareRow(label = "Time Fare", amount = fareBreakdown.timeFare)
            
            Divider(modifier = Modifier.padding(vertical = 8.dp))
            
            Row(
                modifier = Modifier.fillMaxWidth(),
                horizontalArrangement = Arrangement.SpaceBetween
            ) {
                Text(
                    text = "Total",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold
                )
                Text(
                    text = "₹${String.format("%.2f", fareBreakdown.total)}",
                    style = MaterialTheme.typography.titleMedium,
                    fontWeight = FontWeight.Bold,
                    color = MaterialTheme.colorScheme.primary
                )
            }
        }
    }
}

@Composable
private fun FareRow(
    label: String,
    amount: Double,
    modifier: Modifier = Modifier
) {
    Row(
        modifier = modifier.fillMaxWidth(),
        horizontalArrangement = Arrangement.SpaceBetween
    ) {
        Text(
            text = label,
            style = MaterialTheme.typography.bodyMedium
        )
        Text(
            text = "₹${String.format("%.2f", amount)}",
            style = MaterialTheme.typography.bodyMedium
        )
    }
}

@Composable
private fun PaymentMethodSelector(
    selectedMethod: PaymentMethod,
    onMethodSelected: (PaymentMethod) -> Unit,
    enabled: Boolean,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier.fillMaxWidth()
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Text(
                text = "Payment Method",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
            
            PaymentMethodOption(
                method = PaymentMethod.RAZORPAY,
                label = "Razorpay",
                selected = selectedMethod == PaymentMethod.RAZORPAY,
                onSelected = { onMethodSelected(PaymentMethod.RAZORPAY) },
                enabled = enabled
            )
            
            PaymentMethodOption(
                method = PaymentMethod.PAYTM,
                label = "Paytm",
                selected = selectedMethod == PaymentMethod.PAYTM,
                onSelected = { onMethodSelected(PaymentMethod.PAYTM) },
                enabled = enabled
            )
            
            PaymentMethodOption(
                method = PaymentMethod.CASH,
                label = "Cash",
                selected = selectedMethod == PaymentMethod.CASH,
                onSelected = { onMethodSelected(PaymentMethod.CASH) },
                enabled = enabled
            )
        }
    }
}

@Composable
private fun PaymentMethodOption(
    method: PaymentMethod,
    label: String,
    selected: Boolean,
    onSelected: () -> Unit,
    enabled: Boolean,
    modifier: Modifier = Modifier
) {
    Row(
        modifier = modifier
            .fillMaxWidth(),
        verticalAlignment = Alignment.CenterVertically
    ) {
        RadioButton(
            selected = selected,
            onClick = onSelected,
            enabled = enabled
        )
        Spacer(modifier = Modifier.width(8.dp))
        Text(
            text = label,
            style = MaterialTheme.typography.bodyLarge
        )
    }
}

@Composable
private fun PaymentSuccessCard(
    onViewReceipt: () -> Unit,
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
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Icon(
                imageVector = Icons.Default.CheckCircle,
                contentDescription = "Success",
                tint = MaterialTheme.colorScheme.primary,
                modifier = Modifier.size(48.dp)
            )
            Text(
                text = "Payment Successful!",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold,
                color = MaterialTheme.colorScheme.onPrimaryContainer
            )
            TextButton(onClick = onViewReceipt) {
                Text("View Receipt")
            }
        }
    }
}

@Composable
private fun PaymentErrorCard(
    error: String,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier.fillMaxWidth(),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.errorContainer
        )
    ) {
        Row(
            modifier = Modifier.padding(16.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Icon(
                imageVector = Icons.Default.Error,
                contentDescription = "Error",
                tint = MaterialTheme.colorScheme.error
            )
            Text(
                text = error,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onErrorContainer
            )
        }
    }
}
