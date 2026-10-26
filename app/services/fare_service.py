"""
Fare Service for Pan-India Ride-Hailing & Parcel Delivery.
Supports tiered distance rates, surge multipliers, GST (5%), and vehicle categories.
Requirements: 5.1, 5.2, 5.3, 16.3, 16.8, 17.4, 17.5, 17.6, 18.4, 18.9
"""
from typing import Dict, Any, Optional
from app.config import settings
from app.services.india_geo import calculate_haversine_distance


class FareService:
    """Calculates ride and parcel delivery fares across all vehicle categories."""

    @staticmethod
    def calculate_ride_quotes(
        pickup_lat: float,
        pickup_lon: float,
        dropoff_lat: float,
        dropoff_lon: float,
        surge_multiplier: float = 1.0,
        is_night: bool = False
    ) -> Dict[str, Any]:
        """
        Calculates estimated fare across all vehicle types for a given journey in India.
        """
        distance_km = calculate_haversine_distance(pickup_lat, pickup_lon, dropoff_lat, dropoff_lon)
        # Ensure minimum distance
        distance_km = max(1.0, distance_km)
        
        # Estimate duration: ~25 km/h in Indian city traffic, ~60 km/h outstation
        is_outstation = distance_km > 60.0
        avg_speed = 55.0 if is_outstation else 25.0
        duration_minutes = max(5, int((distance_km / avg_speed) * 60))
        
        quotes = {}
        for vehicle_key, spec in settings.vehicle_types.items():
            # Skip outstation category for short city trips under 30km
            if vehicle_key == "outstation" and distance_km < 30.0:
                continue
                
            base = spec["base_fare"]
            per_km = spec["per_km_rate"]
            per_min = spec["per_min_rate"]
            
            # Tiered distance pricing for extended / long trips (>25km gives volume discount)
            if distance_km > 25.0:
                tier1_dist = 25.0
                tier2_dist = distance_km - 25.0
                dist_cost = (tier1_dist * per_km) + (tier2_dist * (per_km * 0.85))
            else:
                dist_cost = distance_km * per_km
                
            time_cost = duration_minutes * per_min
            subtotal = (base + dist_cost + time_cost) * surge_multiplier
            
            # Night charges (11 PM - 5 AM: 10% premium in India)
            if is_night:
                subtotal *= 1.10
                
            # Floor to minimum fare
            subtotal = max(spec["min_fare"], subtotal)
            
            # 5% GST
            gst = round(subtotal * settings.gst_rate, 2)
            total_fare = round(subtotal + gst)
            
            # ETA in minutes for pickup (typically 2 - 8 mins in Indian cities)
            pickup_eta = 2 if vehicle_key == "bike" else (4 if vehicle_key == "auto" else 6)
            
            quotes[vehicle_key] = {
                "key": vehicle_key,
                "name": spec["name"],
                "icon": spec["icon"],
                "description": spec["description"],
                "capacity": spec["capacity"],
                "base_fare": base,
                "distance_fare": round(dist_cost, 2),
                "time_fare": round(time_cost, 2),
                "subtotal": round(subtotal, 2),
                "gst": gst,
                "total_fare": total_fare,
                "currency": "INR",
                "symbol": "₹",
                "pickup_eta_min": pickup_eta
            }
            
        return {
            "distance_km": distance_km,
            "estimated_duration_min": duration_minutes,
            "surge_multiplier": surge_multiplier,
            "is_outstation": is_outstation,
            "quotes": quotes
        }

    @staticmethod
    def calculate_parcel_fare(
        pickup_lat: float,
        pickup_lon: float,
        dropoff_lat: float,
        dropoff_lon: float,
        parcel_size: str = "small",
        weight_kg: float = 2.0,
        is_urgent: bool = False,
        is_fragile: bool = False
    ) -> Dict[str, Any]:
        """
        Calculates fare for peer-to-peer parcel delivery according to Requirement 17.
        Small (up to 5kg): ₹40 base + ₹8/km
        Medium (5-15kg): ₹60 base + ₹10/km
        Large (15-30kg): ₹80 base + ₹12/km
        """
        if weight_kg > 30.0:
            raise ValueError("Parcel exceeds maximum allowable weight limit of 30 kg.")
            
        distance_km = calculate_haversine_distance(pickup_lat, pickup_lon, dropoff_lat, dropoff_lon)
        distance_km = max(1.0, distance_km)
        
        # Determine parcel specs
        size_key = parcel_size.lower()
        if size_key not in settings.parcel_types:
            size_key = "small" if weight_kg <= 5 else ("medium" if weight_kg <= 15 else "large")
            
        spec = settings.parcel_types[size_key]
        base = spec["base_fare"]
        km_rate = spec["per_km_rate"]
        
        dist_charge = distance_km * km_rate
        subtotal = base + dist_charge
        
        # Urgent priority delivery (+25%)
        if is_urgent:
            subtotal += 25.0
            
        # Fragile special care fee (+15%)
        if is_fragile:
            subtotal += 20.0
            
        gst = round(subtotal * settings.gst_rate, 2)
        total = round(subtotal + gst)
        
        est_delivery_hrs = round(max(0.5, (distance_km / 22.0)), 1)
        
        return {
            "parcel_size": size_key,
            "size_name": spec["name"],
            "weight_kg": weight_kg,
            "distance_km": distance_km,
            "base_fare": base,
            "per_km_rate": km_rate,
            "distance_cost": round(dist_charge, 2),
            "urgent_fee": 25.0 if is_urgent else 0.0,
            "fragile_fee": 20.0 if is_fragile else 0.0,
            "subtotal": round(subtotal, 2),
            "gst": gst,
            "total_fare": total,
            "estimated_delivery_hours": est_delivery_hrs,
            "currency": "INR",
            "symbol": "₹"
        }
