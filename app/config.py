"""
Pan-India Configuration & Settings for RideConnect Platform.
Covers all 28 States and 8 Union Territories with 50+ major cities.
"""
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Dict, Any, List


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    app_name: str = Field(default="RideConnect India", alias="APP_NAME")
    app_env: str = Field(default="development", alias="APP_ENV")
    debug: bool = Field(default=True, alias="DEBUG")
    secret_key: str = Field(default="super-secret-india-rideconnect-key-2026", alias="SECRET_KEY")
    
    # Server
    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")
    
    # Database (Default to SQLite for instant plug-and-play, supports PostgreSQL)
    database_url: str = Field(default="sqlite:///./rideconnect_india.db", alias="DATABASE_URL")
    
    # Fare Rates (in Indian Rupees ₹)
    vehicle_types: Dict[str, Dict[str, Any]] = {
        "bike": {
            "name": "Moto / Bike Taxi",
            "icon": "motorcycle",
            "description": "Fastest solo ride through traffic",
            "base_fare": 20.0,
            "per_km_rate": 7.0,
            "per_min_rate": 1.0,
            "min_fare": 25.0,
            "capacity": 1
        },
        "auto": {
            "name": "Auto-Rickshaw",
            "icon": "bus-simple",
            "description": "Affordable 3-wheeler Indian classic",
            "base_fare": 25.0,
            "per_km_rate": 9.5,
            "per_min_rate": 1.2,
            "min_fare": 30.0,
            "capacity": 3
        },
        "mini": {
            "name": "Mini Hatchback",
            "icon": "car-side",
            "description": "Pocket-friendly AC cab for daily trips",
            "base_fare": 40.0,
            "per_km_rate": 12.0,
            "per_min_rate": 1.5,
            "min_fare": 50.0,
            "capacity": 4
        },
        "sedan": {
            "name": "Prime Sedan",
            "icon": "car",
            "description": "Spacious comfortable sedans with top drivers",
            "base_fare": 60.0,
            "per_km_rate": 15.0,
            "per_min_rate": 2.0,
            "min_fare": 80.0,
            "capacity": 4
        },
        "suv": {
            "name": "SUV / XL",
            "icon": "van-shuttle",
            "description": "6-seater Innova/Ertiga for family & luggage",
            "base_fare": 85.0,
            "per_km_rate": 19.0,
            "per_min_rate": 2.5,
            "min_fare": 120.0,
            "capacity": 6
        },
        "outstation": {
            "name": "Intercity Outstation",
            "icon": "route",
            "description": "City to city long distance with verified highway captains",
            "base_fare": 150.0,
            "per_km_rate": 13.0,
            "per_min_rate": 0.5,
            "min_fare": 500.0,
            "capacity": 4
        }
    }
    
    # Parcel Delivery Fare (Requirement 17)
    parcel_types: Dict[str, Dict[str, Any]] = {
        "small": {
            "name": "Small (Up to 5 kg)",
            "description": "Documents, keys, food, clothes",
            "base_fare": 40.0,
            "per_km_rate": 8.0,
            "max_weight_kg": 5.0
        },
        "medium": {
            "name": "Medium (5 to 15 kg)",
            "description": "Electronics, gift boxes, cartons",
            "base_fare": 60.0,
            "per_km_rate": 10.0,
            "max_weight_kg": 15.0
        },
        "large": {
            "name": "Large (15 to 30 kg)",
            "description": "Luggage, appliances, heavy packages",
            "base_fare": 80.0,
            "per_km_rate": 12.0,
            "max_weight_kg": 30.0
        }
    }
    
    # Taxes & Platform Fee
    gst_rate: float = 0.05  # 5% GST for transportation in India
    platform_commission: float = 0.10  # 10% commission
    scheduled_cancellation_fee: float = 30.0  # ₹30 if cancelled <1 hr (Requirement 16)

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
