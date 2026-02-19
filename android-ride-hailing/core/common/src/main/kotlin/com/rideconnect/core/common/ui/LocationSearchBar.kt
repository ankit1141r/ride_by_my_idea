package com.rideconnect.core.common.ui

import androidx.compose.animation.AnimatedVisibility
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Clear
import androidx.compose.material.icons.filled.LocationOn
import androidx.compose.material.icons.filled.Search
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalSoftwareKeyboardController
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.unit.dp
import com.rideconnect.core.domain.model.Place

/**
 * Location search bar with autocomplete functionality.
 * Displays search results from Google Places API.
 * 
 * Requirements: 18.3, 18.4
 * 
 * @param query Current search query
 * @param onQueryChange Callback when query changes
 * @param searchResults List of place search results
 * @param onPlaceSelected Callback when a place is selected
 * @param onSearch Callback to trigger search
 * @param isLoading Whether search is in progress
 * @param modifier Modifier for the search bar
 * @param placeholder Placeholder text for the search field
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun LocationSearchBar(
    query: String,
    onQueryChange: (String) -> Unit,
    searchResults: List<Place>,
    onPlaceSelected: (Place) -> Unit,
    onSearch: (String) -> Unit,
    isLoading: Boolean = false,
    modifier: Modifier = Modifier,
    placeholder: String = "Search location"
) {
    val keyboardController = LocalSoftwareKeyboardController.current
    var isExpanded by remember { mutableStateOf(false) }
    
    // Expand when there are results and query is not empty
    LaunchedEffect(searchResults, query) {
        isExpanded = searchResults.isNotEmpty() && query.isNotEmpty()
    }
    
    Column(modifier = modifier) {
        OutlinedTextField(
            value = query,
            onValueChange = {
                onQueryChange(it)
                if (it.length >= 3) {
                    onSearch(it)
                }
            },
            modifier = Modifier.fillMaxWidth(),
            placeholder = { Text(placeholder) },
            leadingIcon = {
                Icon(
                    imageVector = Icons.Default.Search,
                    contentDescription = "Search"
                )
            },
            trailingIcon = {
                if (query.isNotEmpty()) {
                    IconButton(onClick = {
                        onQueryChange("")
                        isExpanded = false
                    }) {
                        Icon(
                            imageVector = Icons.Default.Clear,
                            contentDescription = "Clear"
                        )
                    }
                }
            },
            singleLine = true,
            keyboardOptions = KeyboardOptions(
                imeAction = ImeAction.Search
            ),
            keyboardActions = KeyboardActions(
                onSearch = {
                    onSearch(query)
                    keyboardController?.hide()
                }
            ),
            colors = OutlinedTextFieldDefaults.colors()
        )
        
        // Search results dropdown
        AnimatedVisibility(visible = isExpanded) {
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .heightIn(max = 300.dp),
                elevation = CardDefaults.cardElevation(defaultElevation = 4.dp)
            ) {
                if (isLoading) {
                    Box(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(16.dp),
                        contentAlignment = Alignment.Center
                    ) {
                        CircularProgressIndicator()
                    }
                } else {
                    LazyColumn {
                        items(searchResults) { place ->
                            LocationSearchResultItem(
                                place = place,
                                onClick = {
                                    onPlaceSelected(place)
                                    isExpanded = false
                                    keyboardController?.hide()
                                }
                            )
                        }
                    }
                }
            }
        }
    }
}

/**
 * Individual search result item.
 */
@Composable
private fun LocationSearchResultItem(
    place: Place,
    onClick: () -> Unit,
    modifier: Modifier = Modifier
) {
    Row(
        modifier = modifier
            .fillMaxWidth()
            .clickable(onClick = onClick)
            .padding(16.dp),
        verticalAlignment = Alignment.CenterVertically
    ) {
        Icon(
            imageVector = Icons.Default.LocationOn,
            contentDescription = null,
            tint = MaterialTheme.colorScheme.primary
        )
        
        Spacer(modifier = Modifier.width(16.dp))
        
        Column(modifier = Modifier.weight(1f)) {
            Text(
                text = place.name,
                style = MaterialTheme.typography.bodyLarge
            )
            Text(
                text = place.address,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}
