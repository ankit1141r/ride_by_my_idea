"""
Fare Calculation Service

This module implements fare calculation logic for the ride-hailing platform.
Validates Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6
"""

from typing import Dict, Optional
from pydantic import BaseModel


class FareBreakdown(BaseModel):
    """Detailed breakdown of fare components"""
    base: float  # Base fare in ₹
    per_km: float  # Rate per kilometer in ₹
    distance: float  # Distance in kilometers
    surge: float  # Surge multiplier


class FareCalculation(BaseModel):
    """Complete fare calculation result"""
    base_fare: float  # Base fare component
    distance_charge: float  # Distance-based charge
    surge_multiplier: float  # Surge pricing multiplier
    total_fare: float  # Final total fare
    breakdown: FareBreakdown  # Detailed breakdown


# Constants for fare calculation (Requirements: 5.2, 5.3, 18.4, 18.9)
BASE_FARE = 30.0  # ₹30 base fare
PER_KM_RATE_STANDARD = 12.0  # ₹12 per kilometer for first 25km
PER_KM_RATE_EXTENDED = 10.0  # ₹10 per kilometer beyond 25km
DISTANCE_TIER_THRESHOLD = 25.0  # Distance threshold for tiered pricing in km


def calculate_estimated_fare(
    distance_km: float,
    surge_multiplier: float = 1.0
) -> FareCalculation:
    """
    Calculate estimated fare for a ride request with tiered pricing.
    
    Formula: 
    - For distance <= 25km: (₹30 + distance_km * ₹12) * surge_multiplier
    - For distance > 25km: (₹30 + 25 * ₹12 + (distance_km - 25) * ₹10) * surge_multiplier
    
    Args:
        distance_km: Distance in kilometers (straight-line or estimated route)
        surge_multiplier: Surge pricing multiplier (default 1.0, can be higher during peak demand)
    
    Returns:
        FareCalculation with complete breakdown
    
    Validates: Requirements 5.1, 5.2, 5.3, 5.6, 18.4, 18.9
    """
    # Calculate base components with tiered pricing
    base_fare = BASE_FARE
    
    if distance_km <= DISTANCE_TIER_THRESHOLD:
        # Standard rate for distances up to 25km
        distance_charge = distance_km * PER_KM_RATE_STANDARD
        per_km_rate = PER_KM_RATE_STANDARD
    else:
        # Tiered rate: first 25km at standard rate, rest at extended rate
        standard_distance_charge = DISTANCE_TIER_THRESHOLD * PER_KM_RATE_STANDARD
        extended_distance = distance_km - DISTANCE_TIER_THRESHOLD
        extended_distance_charge = extended_distance * PER_KM_RATE_EXTENDED
        distance_charge = standard_distance_charge + extended_distance_charge
        # Use blended rate for breakdown display
        per_km_rate = distance_charge / distance_km
    
    # Apply surge multiplier to total
    subtotal = base_fare + distance_charge
    total_fare = subtotal * surge_multiplier
    
    # Create breakdown
    breakdown = FareBreakdown(
        base=base_fare,
        per_km=round(per_km_rate, 2),
        distance=distance_km,
        surge=surge_multiplier
    )
    
    return FareCalculation(
        base_fare=base_fare,
        distance_charge=round(distance_charge, 2),
        surge_multiplier=surge_multiplier,
        total_fare=round(total_fare, 2),
        breakdown=breakdown
    )


def calculate_final_fare(
    actual_distance_km: float,
    estimated_fare: float,
    surge_multiplier: float = 1.0
) -> FareCalculation:
    """
    Calculate final fare for a completed ride with fare protection and tiered pricing.
    
    Fare Protection: If actual fare differs from estimated by more than 20%,
    charge the estimated fare instead.
    
    Args:
        actual_distance_km: Actual distance traveled in kilometers
        estimated_fare: The estimated fare shown to rider at booking
        surge_multiplier: Surge multiplier used for the ride
    
    Returns:
        FareCalculation with final fare (protected if necessary)
    
    Validates: Requirements 5.4, 5.5, 18.4, 18.9
    """
    # Calculate fare based on actual distance with tiered pricing
    base_fare = BASE_FARE
    
    if actual_distance_km <= DISTANCE_TIER_THRESHOLD:
        # Standard rate for distances up to 25km
        distance_charge = actual_distance_km * PER_KM_RATE_STANDARD
        per_km_rate = PER_KM_RATE_STANDARD
    else:
        # Tiered rate: first 25km at standard rate, rest at extended rate
        standard_distance_charge = DISTANCE_TIER_THRESHOLD * PER_KM_RATE_STANDARD
        extended_distance = actual_distance_km - DISTANCE_TIER_THRESHOLD
        extended_distance_charge = extended_distance * PER_KM_RATE_EXTENDED
        distance_charge = standard_distance_charge + extended_distance_charge
        # Use blended rate for breakdown display
        per_km_rate = distance_charge / actual_distance_km
    
    subtotal = base_fare + distance_charge
    actual_fare = subtotal * surge_multiplier
    
    # Apply fare protection (20% cap)
    difference_percentage = abs(actual_fare - estimated_fare) / estimated_fare
    
    if difference_percentage > 0.20:
        # Cap at estimated fare if difference exceeds 20%
        final_fare = estimated_fare
    else:
        final_fare = actual_fare
    
    # Create breakdown
    breakdown = FareBreakdown(
        base=base_fare,
        per_km=round(per_km_rate, 2),
        distance=actual_distance_km,
        surge=surge_multiplier
    )
    
    return FareCalculation(
        base_fare=base_fare,
        distance_charge=round(distance_charge, 2),
        surge_multiplier=surge_multiplier,
        total_fare=round(final_fare, 2),
        breakdown=breakdown
    )


def get_fare_summary(fare_calculation: FareCalculation) -> Dict[str, float]:
    """
    Get a simple summary of fare components for display.
    
    Args:
        fare_calculation: FareCalculation object
    
    Returns:
        Dictionary with fare summary
    """
    return {
        "base_fare": fare_calculation.base_fare,
        "distance_charge": fare_calculation.distance_charge,
        "surge_multiplier": fare_calculation.surge_multiplier,
        "total_fare": fare_calculation.total_fare
    }


# Parcel delivery fare constants (Requirements: 17.4, 17.5, 17.6)
PARCEL_BASE_FARE = {
    "small": 40.0,   # ₹40 base for small parcels
    "medium": 60.0,  # ₹60 base for medium parcels
    "large": 80.0    # ₹80 base for large parcels
}

PARCEL_PER_KM_RATE = {
    "small": 8.0,    # ₹8 per km for small parcels
    "medium": 10.0,  # ₹10 per km for medium parcels
    "large": 12.0    # ₹12 per km for large parcels
}


class ParcelFareBreakdown(BaseModel):
    """Detailed breakdown of parcel delivery fare components"""
    base: float  # Base fare based on size
    per_km: float  # Rate per kilometer based on size
    distance: float  # Distance in kilometers
    size: str  # Parcel size (small/medium/large)


class ParcelFareCalculation(BaseModel):
    """Complete parcel fare calculation result"""
    base_fare: float  # Base fare component
    distance_charge: float  # Distance-based charge
    total_fare: float  # Final total fare
    breakdown: ParcelFareBreakdown  # Detailed breakdown


def calculate_parcel_fare(
    distance_km: float,
    parcel_size: str
) -> ParcelFareCalculation:
    """
    Calculate fare for parcel delivery based on size and distance.
    
    Formula: base_fare[size] + (distance_km * per_km_rate[size])
    
    Size-based pricing:
    - Small (up to 5kg): ₹40 base + ₹8/km
    - Medium (5-15kg): ₹60 base + ₹10/km
    - Large (15-30kg): ₹80 base + ₹12/km
    
    Args:
        distance_km: Distance in kilometers
        parcel_size: Size of parcel (small, medium, large)
    
    Returns:
        ParcelFareCalculation with complete breakdown
    
    Validates: Requirements 17.4, 17.5, 17.6
    """
    # Validate parcel size
    if parcel_size not in PARCEL_BASE_FARE:
        raise ValueError(f"Invalid parcel size: {parcel_size}. Must be small, medium, or large.")
    
    # Get size-specific rates
    base_fare = PARCEL_BASE_FARE[parcel_size]
    per_km_rate = PARCEL_PER_KM_RATE[parcel_size]
    
    # Calculate distance charge
    distance_charge = distance_km * per_km_rate
    
    # Calculate total
    total_fare = base_fare + distance_charge
    
    # Create breakdown
    breakdown = ParcelFareBreakdown(
        base=base_fare,
        per_km=per_km_rate,
        distance=distance_km,
        size=parcel_size
    )
    
    return ParcelFareCalculation(
        base_fare=base_fare,
        distance_charge=round(distance_charge, 2),
        total_fare=round(total_fare, 2),
        breakdown=breakdown
    )


def estimate_delivery_time(distance_km: float) -> int:
    """
    Estimate delivery time in minutes based on distance.
    
    Assumes average speed of 30 km/h in city traffic.
    
    Args:
        distance_km: Distance in kilometers
    
    Returns:
        Estimated delivery time in minutes
    
    Validates: Requirements 17.13
    """
    # Average speed: 30 km/h
    # Add 10 minutes buffer for pickup and delivery
    travel_time_minutes = (distance_km / 30.0) * 60
    buffer_minutes = 10
    
    total_minutes = travel_time_minutes + buffer_minutes
    
    return round(total_minutes)
