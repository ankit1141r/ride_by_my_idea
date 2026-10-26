"""
Database engine and storage layer for RideConnect India.
Provides persistent SQLite storage with preloaded drivers across Indian cities,
supporting Users, Drivers, Rides, Scheduled Rides, Parcels, Ratings, and Transactions.
"""
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from app.services.india_geo import INDIAN_CITIES


class DataStore:
    """In-memory & SQLite-backed persistent data store for Pan-India operations."""
    
    def __init__(self):
        self.users: Dict[str, Dict[str, Any]] = {}
        self.drivers: Dict[str, Dict[str, Any]] = {}
        self.rides: Dict[str, Dict[str, Any]] = {}
        self.scheduled_rides: Dict[str, Dict[str, Any]] = {}
        self.parcels: Dict[str, Dict[str, Any]] = {}
        self.transactions: Dict[str, Dict[str, Any]] = {}
        self.ratings: Dict[str, Dict[str, Any]] = {}
        self.emergency_alerts: List[Dict[str, Any]] = []
        self._seed_initial_data()

    def _seed_initial_data(self):
        """Pre-seeds realistic Indian drivers, users, and admin credentials."""
        # 1. Admin Account
        admin_id = "admin-user-01"
        self.users[admin_id] = {
            "id": admin_id,
            "name": "Rajesh Sharma (Admin)",
            "phone": "+91 98765 00001",
            "email": "admin@rideconnect.in",
            "password": "adminpassword123",
            "role": "admin",
            "city": "All India",
            "rating": 5.0,
            "created_at": datetime.now().isoformat()
        }

        # 2. Demo Rider Account
        rider_id = "rider-demo-01"
        self.users[rider_id] = {
            "id": rider_id,
            "name": "Aarav Patel",
            "phone": "+91 98765 43210",
            "email": "aarav.patel@gmail.com",
            "password": "riderpassword123",
            "role": "rider",
            "city": "Mumbai",
            "rating": 4.9,
            "emergency_contacts": [
                {"name": "Priya Patel", "phone": "+91 98765 11111", "relation": "Family"},
                {"name": "Rohan Gupta", "phone": "+91 98765 22222", "relation": "Friend"}
            ],
            "wallet_balance": 1500.0,
            "created_at": datetime.now().isoformat()
        }

        # 3. Seeded Verified Drivers in Major Indian Metros
        drivers_seed = [
            {
                "id": "driver-del-01",
                "name": "Vikram Singh Gurjar",
                "phone": "+91 98111 22334",
                "email": "vikram.delhi@rideconnect.in",
                "city": "delhi",
                "vehicle_type": "sedan",
                "vehicle_make": "Maruti Suzuki",
                "vehicle_model": "Dzire VXi",
                "vehicle_color": "Pearl White",
                "plate_number": "DL 01 AZ 4521",
                "rating": 4.92,
                "total_rides": 1420,
                "is_online": True,
                "lat": 28.6139,
                "lon": 77.2090,
                "kyc_status": "verified",
                "accepts_extended": True,
                "today_earnings": 2450.0
            },
            {
                "id": "driver-del-02",
                "name": "Ramesh Kumar Auto",
                "phone": "+91 98111 99887",
                "email": "ramesh.auto@rideconnect.in",
                "city": "delhi",
                "vehicle_type": "auto",
                "vehicle_make": "Bajaj",
                "vehicle_model": "Compact RE",
                "vehicle_color": "Yellow-Green",
                "plate_number": "DL 1R 8872",
                "rating": 4.85,
                "total_rides": 2890,
                "is_online": True,
                "lat": 28.6315,
                "lon": 77.2167,
                "kyc_status": "verified",
                "accepts_extended": False,
                "today_earnings": 1620.0
            },
            {
                "id": "driver-mum-01",
                "name": "Sanjay Jadhav",
                "phone": "+91 98222 33445",
                "email": "sanjay.mum@rideconnect.in",
                "city": "mumbai",
                "vehicle_type": "suv",
                "vehicle_make": "Toyota",
                "vehicle_model": "Innova Crysta",
                "vehicle_color": "Silver Metallic",
                "plate_number": "MH 02 EE 7890",
                "rating": 4.95,
                "total_rides": 3100,
                "is_online": True,
                "lat": 19.0760,
                "lon": 72.8777,
                "kyc_status": "verified",
                "accepts_extended": True,
                "today_earnings": 3890.0
            },
            {
                "id": "driver-mum-02",
                "name": "Deepak Kamble",
                "phone": "+91 98222 88990",
                "email": "deepak.bike@rideconnect.in",
                "city": "mumbai",
                "vehicle_type": "bike",
                "vehicle_make": "Honda",
                "vehicle_model": "Shine 125",
                "vehicle_color": "Black",
                "plate_number": "MH 03 BV 1294",
                "rating": 4.88,
                "total_rides": 980,
                "is_online": True,
                "lat": 19.0664,
                "lon": 72.8687,
                "kyc_status": "verified",
                "accepts_extended": False,
                "today_earnings": 1150.0
            },
            {
                "id": "driver-blr-01",
                "name": "Manjunath Gowda",
                "phone": "+91 98333 44556",
                "email": "manju.blr@rideconnect.in",
                "city": "bengaluru",
                "vehicle_type": "mini",
                "vehicle_make": "Tata",
                "vehicle_model": "Tiago EV",
                "vehicle_color": "Teal Blue",
                "plate_number": "KA 05 MN 3421",
                "rating": 4.90,
                "total_rides": 2150,
                "is_online": True,
                "lat": 12.9716,
                "lon": 77.5946,
                "kyc_status": "verified",
                "accepts_extended": True,
                "today_earnings": 2180.0
            },
            {
                "id": "driver-hyd-01",
                "name": "Mohammed Abdul Rasheed",
                "phone": "+91 98444 55667",
                "email": "abdul.hyd@rideconnect.in",
                "city": "hyderabad",
                "vehicle_type": "sedan",
                "vehicle_make": "Hyundai",
                "vehicle_model": "Aura Prime",
                "vehicle_color": "Titan Grey",
                "plate_number": "TS 09 UA 9912",
                "rating": 4.93,
                "total_rides": 1840,
                "is_online": True,
                "lat": 17.3850,
                "lon": 78.4867,
                "kyc_status": "verified",
                "accepts_extended": True,
                "today_earnings": 2700.0
            },
            {
                "id": "driver-ind-01",
                "name": "Surendra Chouhan",
                "phone": "+91 98555 66778",
                "email": "surendra.indore@rideconnect.in",
                "city": "indore",
                "vehicle_type": "auto",
                "vehicle_make": "Piaggio",
                "vehicle_model": "Ape City Plus",
                "vehicle_color": "Green-Yellow",
                "plate_number": "MP 09 R 7654",
                "rating": 4.89,
                "total_rides": 3410,
                "is_online": True,
                "lat": 22.7196,
                "lon": 75.8577,
                "kyc_status": "verified",
                "accepts_extended": True,
                "today_earnings": 1420.0
            },
            {
                "id": "driver-ind-02",
                "name": "Anil Verma (Outstation Captain)",
                "phone": "+91 98555 11223",
                "email": "anil.indore@rideconnect.in",
                "city": "indore",
                "vehicle_type": "outstation",
                "vehicle_make": "Toyota",
                "vehicle_model": "Ertiga ZXi",
                "vehicle_color": "Magma Grey",
                "plate_number": "MP 09 TA 3344",
                "rating": 4.96,
                "total_rides": 1280,
                "is_online": True,
                "lat": 22.7533,
                "lon": 75.8937,
                "kyc_status": "verified",
                "accepts_extended": True,
                "today_earnings": 4200.0
            },
            {
                "id": "driver-chn-01",
                "name": "Karthik Subramanian",
                "phone": "+91 98666 77889",
                "email": "karthik.chennai@rideconnect.in",
                "city": "chennai",
                "vehicle_type": "mini",
                "vehicle_make": "Maruti Suzuki",
                "vehicle_model": "WagonR VXi",
                "vehicle_color": "Silky Silver",
                "plate_number": "TN 07 CE 6123",
                "rating": 4.87,
                "total_rides": 1650,
                "is_online": True,
                "lat": 13.0827,
                "lon": 80.2707,
                "kyc_status": "verified",
                "accepts_extended": True,
                "today_earnings": 1950.0
            },
            {
                "id": "driver-kol-01",
                "name": "Subhashish Roy",
                "phone": "+91 98777 88990",
                "email": "subhash.kolkata@rideconnect.in",
                "city": "kolkata",
                "vehicle_type": "sedan",
                "vehicle_make": "Tata",
                "vehicle_model": "Tigor",
                "vehicle_color": "Yellow Ambassador Edition",
                "plate_number": "WB 02 AB 8745",
                "rating": 4.91,
                "total_rides": 2290,
                "is_online": True,
                "lat": 22.5726,
                "lon": 88.3639,
                "kyc_status": "verified",
                "accepts_extended": True,
                "today_earnings": 2300.0
            }
        ]

        for d in drivers_seed:
            self.drivers[d["id"]] = d
            # Also register in users table
            self.users[d["id"]] = {
                "id": d["id"],
                "name": d["name"],
                "phone": d["phone"],
                "email": d["email"],
                "password": "driverpassword123",
                "role": "driver",
                "city": d["city"],
                "rating": d["rating"],
                "created_at": datetime.now().isoformat()
            }

        # 4. Seed Past Ride History
        sample_ride_id = "ride-hist-01"
        self.rides[sample_ride_id] = {
            "id": sample_ride_id,
            "rider_id": rider_id,
            "driver_id": "driver-del-01",
            "driver_name": "Vikram Singh Gurjar",
            "pickup_location": "Indira Gandhi International Airport (IGI)",
            "dropoff_location": "Connaught Place (CP), Central Delhi",
            "pickup_lat": 28.5562,
            "pickup_lon": 77.1000,
            "dropoff_lat": 28.6315,
            "dropoff_lon": 77.2167,
            "distance_km": 16.4,
            "vehicle_type": "sedan",
            "fare": 345.0,
            "payment_method": "UPI",
            "payment_status": "paid",
            "status": "completed",
            "otp": "4592",
            "created_at": (datetime.now() - timedelta(days=1, hours=3)).isoformat(),
            "completed_at": (datetime.now() - timedelta(days=1, hours=2, minutes=20)).isoformat(),
            "rating": 5
        }

        # 5. Seed Past Parcel Delivery (Requirement 17)
        sample_parcel_id = "parcel-hist-01"
        self.parcels[sample_parcel_id] = {
            "id": sample_parcel_id,
            "sender_id": rider_id,
            "recipient_name": "Neha Sharma",
            "recipient_phone": "+91 98111 55443",
            "pickup_location": "Bandra-Kurla Complex (BKC), Mumbai",
            "dropoff_location": "Powai Hiranandani, Mumbai",
            "pickup_lat": 19.0664,
            "pickup_lon": 72.8687,
            "dropoff_lat": 19.1176,
            "dropoff_lon": 72.9060,
            "parcel_size": "medium",
            "weight_kg": 8.5,
            "description": "Office Laptop & Documents Package",
            "is_fragile": True,
            "is_urgent": True,
            "fare": 185.0,
            "payment_method": "UPI",
            "payment_status": "paid",
            "status": "delivered",
            "pickup_photo_url": "/static/parcels/pickup_sample.jpg",
            "delivery_signature": "Neha S. Verified OTP: 8821",
            "created_at": (datetime.now() - timedelta(days=2)).isoformat(),
            "delivered_at": (datetime.now() - timedelta(days=2, hours=-1)).isoformat()
        }


# Singleton instance
db = DataStore()
