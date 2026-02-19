package com.rideconnect.core.common.ui

import android.net.Uri
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.Image
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.*
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import coil.compose.rememberAsyncImagePainter
import com.rideconnect.core.domain.viewmodel.PhotoUploadState
import com.rideconnect.core.domain.viewmodel.ProfileState
import com.rideconnect.core.domain.viewmodel.ProfileViewModel
import java.io.File
import java.io.FileOutputStream

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ProfileScreen(
    viewModel: ProfileViewModel = hiltViewModel(),
    onNavigateToEmergencyContacts: () -> Unit = {},
    onNavigateToVehicleDetails: () -> Unit = {},
    isDriver: Boolean = false
) {
    val user by viewModel.user.collectAsState()
    val profileState by viewModel.profileState.collectAsState()
    val photoUploadState by viewModel.photoUploadState.collectAsState()
    val context = LocalContext.current
    
    var showEditDialog by remember { mutableStateOf(false) }
    var editName by remember { mutableStateOf("") }
    var editEmail by remember { mutableStateOf("") }
    
    val photoPickerLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.GetContent()
    ) { uri: Uri? ->
        uri?.let {
            // Copy URI to file and upload
            val file = File(context.cacheDir, "profile_photo_${System.currentTimeMillis()}.jpg")
            context.contentResolver.openInputStream(uri)?.use { input ->
                FileOutputStream(file).use { output ->
                    input.copyTo(output)
                }
            }
            viewModel.uploadProfilePhoto(file)
        }
    }
    
    LaunchedEffect(Unit) {
        viewModel.loadProfile()
    }
    
    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Profile") },
                actions = {
                    IconButton(onClick = {
                        editName = user?.name ?: ""
                        editEmail = user?.email ?: ""
                        showEditDialog = true
                    }) {
                        Icon(Icons.Default.Edit, contentDescription = "Edit Profile")
                    }
                }
            )
        }
    ) { paddingValues ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(paddingValues)
        ) {
            Column(
                modifier = Modifier
                    .fillMaxSize()
                    .verticalScroll(rememberScrollState())
                    .padding(16.dp),
                horizontalAlignment = Alignment.CenterHorizontally
            ) {
                // Profile Photo
                Box(
                    modifier = Modifier
                        .size(120.dp)
                        .clip(CircleShape)
                        .clickable { photoPickerLauncher.launch("image/*") }
                ) {
                    if (user?.profilePhotoUrl != null) {
                        Image(
                            painter = rememberAsyncImagePainter(user?.profilePhotoUrl),
                            contentDescription = "Profile Photo",
                            modifier = Modifier.fillMaxSize(),
                            contentScale = ContentScale.Crop
                        )
                    } else {
                        Surface(
                            modifier = Modifier.fillMaxSize(),
                            color = MaterialTheme.colorScheme.primaryContainer
                        ) {
                            Icon(
                                imageVector = Icons.Default.Person,
                                contentDescription = "Default Profile",
                                modifier = Modifier
                                    .fillMaxSize()
                                    .padding(24.dp),
                                tint = MaterialTheme.colorScheme.onPrimaryContainer
                            )
                        }
                    }
                    
                    // Upload indicator
                    if (photoUploadState is PhotoUploadState.Uploading) {
                        CircularProgressIndicator(
                            modifier = Modifier
                                .align(Alignment.Center)
                                .size(40.dp)
                        )
                    }
                }
                
                Spacer(modifier = Modifier.height(8.dp))
                
                Text(
                    text = "Tap to change photo",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant
                )
                
                Spacer(modifier = Modifier.height(24.dp))
                
                // User Info
                user?.let { userData ->
                    ProfileInfoCard(
                        title = "Name",
                        value = userData.name,
                        icon = Icons.Default.Person
                    )
                    
                    Spacer(modifier = Modifier.height(8.dp))
                    
                    ProfileInfoCard(
                        title = "Phone",
                        value = userData.phoneNumber,
                        icon = Icons.Default.Phone
                    )
                    
                    Spacer(modifier = Modifier.height(8.dp))
                    
                    ProfileInfoCard(
                        title = "Email",
                        value = userData.email ?: "Not set",
                        icon = Icons.Default.Email
                    )
                    
                    Spacer(modifier = Modifier.height(8.dp))
                    
                    ProfileInfoCard(
                        title = "Rating",
                        value = String.format("%.1f ⭐", userData.rating),
                        icon = Icons.Default.Star
                    )
                }
                
                Spacer(modifier = Modifier.height(24.dp))
                
                // Action Buttons
                OutlinedCard(
                    modifier = Modifier.fillMaxWidth(),
                    onClick = onNavigateToEmergencyContacts
                ) {
                    ListItem(
                        headlineContent = { Text("Emergency Contacts") },
                        leadingContent = {
                            Icon(Icons.Default.Warning, contentDescription = null)
                        },
                        trailingContent = {
                            Icon(Icons.Default.KeyboardArrowRight, contentDescription = null)
                        }
                    )
                }
                
                if (isDriver) {
                    Spacer(modifier = Modifier.height(8.dp))
                    
                    OutlinedCard(
                        modifier = Modifier.fillMaxWidth(),
                        onClick = onNavigateToVehicleDetails
                    ) {
                        ListItem(
                            headlineContent = { Text("Vehicle Details") },
                            leadingContent = {
                                Icon(Icons.Default.DirectionsCar, contentDescription = null)
                            },
                            trailingContent = {
                                Icon(Icons.Default.KeyboardArrowRight, contentDescription = null)
                            }
                        )
                    }
                }
            }
            
            // Loading indicator
            if (profileState is ProfileState.Loading) {
                CircularProgressIndicator(
                    modifier = Modifier.align(Alignment.Center)
                )
            }
        }
    }
    
    // Edit Profile Dialog
    if (showEditDialog) {
        AlertDialog(
            onDismissRequest = { showEditDialog = false },
            title = { Text("Edit Profile") },
            text = {
                Column {
                    OutlinedTextField(
                        value = editName,
                        onValueChange = { editName = it },
                        label = { Text("Name") },
                        modifier = Modifier.fillMaxWidth()
                    )
                    
                    Spacer(modifier = Modifier.height(8.dp))
                    
                    OutlinedTextField(
                        value = editEmail,
                        onValueChange = { editEmail = it },
                        label = { Text("Email") },
                        modifier = Modifier.fillMaxWidth()
                    )
                }
            },
            confirmButton = {
                TextButton(
                    onClick = {
                        viewModel.updateProfile(
                            name = editName.takeIf { it.isNotBlank() },
                            email = editEmail.takeIf { it.isNotBlank() }
                        )
                        showEditDialog = false
                    }
                ) {
                    Text("Save")
                }
            },
            dismissButton = {
                TextButton(onClick = { showEditDialog = false }) {
                    Text("Cancel")
                }
            }
        )
    }
    
    // Error Snackbar
    LaunchedEffect(profileState) {
        if (profileState is ProfileState.Error) {
            // Show error message
            viewModel.resetState()
        }
    }
    
    LaunchedEffect(photoUploadState) {
        if (photoUploadState is PhotoUploadState.Error) {
            // Show error message
            viewModel.resetPhotoUploadState()
        }
    }
}

@Composable
fun ProfileInfoCard(
    title: String,
    value: String,
    icon: androidx.compose.ui.graphics.vector.ImageVector
) {
    OutlinedCard(
        modifier = Modifier.fillMaxWidth()
    ) {
        ListItem(
            headlineContent = { Text(value) },
            supportingContent = { Text(title) },
            leadingContent = {
                Icon(icon, contentDescription = null)
            }
        )
    }
}
