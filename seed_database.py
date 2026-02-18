#!/usr/bin/env python3
"""
Database seeding script for RideConnect platform.
Creates fake users, drivers, and sample data for testing.
"""

import asyncio
import random
from datetime import datetime, timedelta
from typing import List
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

from app.database import get_async_session
from app.models.user import User, DriverProfile
from app.models.ride import Ride
from app.models.transaction import Transaction, DriverPayout
from app.models.verification import VerificationSession
from app.models.location import Location
from app.config import settings

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Sample data
INDIAN_NAMES = [
    "Rahul Sharma", "Priya Patel", "Amit Kumar", "Sneha Singh", "Vikash Gupta",
    "Anita Verma", "Rajesh Yadav", "Pooja Agarwal", "Suresh Jain", "Kavita Mehta",
    "Deepak Tiwari", "Ritu Saxena", "Manoj Pandey", "Sunita Chouhan", "Arun Malhotra",
    "Geeta Soni", "Vinod Shukla", "Meera Joshi", "Sanjay Dubey", "Nisha Bansal",
    "Ramesh Gupta", "Kiran Sharma", "Ashok Verma", "Seema Agrawal", "Dinesh Kumar"
]

INDORE_LOCATIONS = [
    {"name": "Rajwada", "lat": 22.7196, "lon": 75.8577},
    {"name": "Sarafa Bazaar", "lat": 22.7205, "lon": 75.8573},
    {"name": "Palasia Square", "lat": 22.7280, "lon": 75.8723},
    {"name": "Vijay Nagar", "lat": 22.7532, "lon": 75.8937},
    {"name": "Bhawar Kuan", "lat": 22.6890, "lon": 75.8567},
    {"name": "Treasure Island Mall", "lat": 22.7244, "lon": 75.9063},
    {"name": "Phoenix Citadel Mall", "lat": 22.7458, "lon": 75.9017},
    {"name": "Indore Railway Station", "lat": 22.7179, "lon": 75.8333},
    {"name": "Devi Ahilya Vishwavidyalaya", "lat": 22.6868, "lon": 75.8333},
    {"name": "Holkar Stadium", "lat": 22.7244, "lon": 75.8723},
    {"name": "Lal Bagh Palace", "lat": 22.6947, "lon": 75.8613},
    {"name": "Central Mall", "lat": 22.7280, "lon": 75.8723},
    {"name": "Orbit Mall", "lat": 22.7458, "lon": 75.9017},
    {"name": "Brilliant Convention Centre", "lat": 22.7532, "lon": 75.8937},
    {"name": "Khajrana Ganesh Temple", "lat": 22.6890, "lon": 75.8567}
]

VEHICLE_MAKES_MODELS = [
    {"make": "Maruti Suzuki", "models": ["Swift", "Dzire", "Alto", "Wagon R", "Baleno"]},
    {"make": "Hyundai", "models": ["i20", "Verna", "Creta", "Grand i10", "Santro"]},
    {"make": "Tata", "models": ["Nexon", "Tiago", "Harrier", "Altroz", "Punch"]},
    {"make": "Mahindra", "models": ["Scorpio", "XUV300", "Bolero", "Thar", "KUV100"]},
    {"make": "Honda", "models": ["City", "Amaze", "Jazz", "WR-V", "Civic"]},
    {"make": "Toyota", "models": ["Innova", "Fortuner", "Etios", "Glanza", "Urban Cruiser"]}
]

COLORS = ["White", "Silver", "Black", "Red", "Blue", "Grey", "Brown"]

def generate_phone_number() -> str:
    """Generate a valid Indian phone number."""
    return f"+91{random.randint(6000000000, 9999999999)}"

def generate_registration_number() -> str:
    """Generate a valid Indian vehicle registration number."""
    state_codes = ["MP", "MH", "DL", "KA", "TN", "GJ", "RJ", "UP"]
    state = random.choice(state_codes)
    district = random.randint(1, 99)
    series = ''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=2))
    number = random.randint(1000, 9999)
    return f"{state}{district:02d}{series}{number}"

def generate_license_number() -> str:
    """Generate a valid Indian driving license number."""
    state_codes = ["MP", "MH", "DL", "KA", "TN", "GJ", "RJ", "UP"]
    state = random.choice(state_codes)
    rto = random.randint(1, 99)
    year = random.randint(80, 99)
    number = random.randint(1000000, 9999999)
    return f"{state}{rto:02d}{year:02d}{number:07d}"

async def create_users(session: AsyncSession, count: int = 50) -> List[User]:
    """Create fake users (riders and drivers)."""
    users = []
    
    for i in range(count):
        name = random.choice(INDIAN_NAMES)
        phone = generate_phone_number()
        
        # Ensure unique phone numbers
        while any(u.phone_number == phone for u in users):
            phone = generate_phone_number()
        
        user_type = "driver" if i < count // 3 else "rider"  # 1/3 drivers, 2/3 riders
        
        user = User(
            id=str(uuid.uuid4()),
            full_name=name,
            phone_number=phone,
            email=f"user{i+1}@example.com",
            password_hash=pwd_context.hash("password123"),
            user_type=user_type,
            is_verified=True,
            is_active=True,
            created_at=datetime.utcnow() - timedelta(days=random.randint(1, 365))
        )
        
        session.add(user)
        users.append(user)
    
    await session.commit()
    print(f"Created {count} users ({len([u for u in users if u.user_type == 'driver'])} drivers, {len([u for u in users if u.user_type == 'rider'])} riders)")
    return users

async def create_driver_profiles(session: AsyncSession, drivers: List[User]) -> List[DriverProfile]:
    """Create driver profiles with vehicles."""
    profiles = []
    
    for driver in drivers:
        if driver.user_type != "driver":
            continue
            
        vehicle_info = random.choice(VEHICLE_MAKES_MODELS)
        model = random.choice(vehicle_info["models"])
        
        profile = DriverProfile(
            user_id=driver.id,
            license_number=generate_license_number(),
            vehicle_registration=generate_registration_number(),
            vehicle_make=vehicle_info["make"],
            vehicle_model=model,
            vehicle_color=random.choice(COLORS),
            insurance_expiry=datetime.utcnow() + timedelta(days=random.randint(30, 365)),
            is_available=random.choice([True, False]),
            is_verified=True,
            current_latitude=22.7196 + random.uniform(-0.1, 0.1),
            current_longitude=75.8577 + random.uniform(-0.1, 0.1),
            last_location_update=datetime.utcnow() - timedelta(minutes=random.randint(1, 60))
        )
        
        session.add(profile)
        profiles.append(profile)
    
    await session.commit()
    print(f"Created {len(profiles)} driver profiles")
    return profiles

async def create_sample_rides(session: AsyncSession, users: List[User], count: int = 100) -> List[Ride]:
    """Create sample rides with various statuses."""
    rides = []
    riders = [u for u in users if u.user_type == "rider"]
    drivers = [u for u in users if u.user_type == "driver"]
    
    statuses = ["completed", "cancelled", "in_progress", "matched", "requested"]
    status_weights = [0.6, 0.2, 0.05, 0.1, 0.05]  # Most rides completed
    
    for i in range(count):
        rider = random.choice(riders)
        pickup_loc = random.choice(INDORE_LOCATIONS)
        dropoff_loc = random.choice(INDORE_LOCATIONS)
        
        # Ensure different pickup and dropoff
        while dropoff_loc == pickup_loc:
            dropoff_loc = random.choice(INDORE_LOCATIONS)
        
        # Calculate distance (approximate)
        distance = random.uniform(2.0, 25.0)
        estimated_fare = 30 + (distance * 12)  # Base fare + per km rate
        
        status = random.choices(statuses, weights=status_weights)[0]
        
        ride = Ride(
            id=str(uuid.uuid4()),
            rider_id=rider.id,
            pickup_latitude=pickup_loc["lat"],
            pickup_longitude=pickup_loc["lon"],
            pickup_address=f"{pickup_loc['name']}, Indore, Madhya Pradesh",
            dropoff_latitude=dropoff_loc["lat"],
            dropoff_longitude=dropoff_loc["lon"],
            dropoff_address=f"{dropoff_loc['name']}, Indore, Madhya Pradesh",
            estimated_fare=round(estimated_fare, 2),
            distance_km=round(distance, 2),
            status=status,
            created_at=datetime.utcnow() - timedelta(days=random.randint(1, 30))
        )
        
        # Assign driver for non-requested rides
        if status != "requested":
            driver = random.choice(drivers)
            ride.driver_id = driver.id
            
            if status == "completed":
                # Add some variation to final fare
                fare_variation = random.uniform(0.9, 1.1)
                ride.final_fare = round(estimated_fare * fare_variation, 2)
                ride.started_at = ride.created_at + timedelta(minutes=random.randint(5, 15))
                ride.completed_at = ride.started_at + timedelta(minutes=random.randint(10, 60))
            elif status == "in_progress":
                ride.started_at = ride.created_at + timedelta(minutes=random.randint(5, 15))
            elif status == "cancelled":
                ride.cancelled_at = ride.created_at + timedelta(minutes=random.randint(1, 30))
                ride.cancellation_reason = random.choice([
                    "Driver not available", "Rider cancelled", "Traffic issues", 
                    "Vehicle breakdown", "Emergency"
                ])
        
        session.add(ride)
        rides.append(ride)
    
    await session.commit()
    print(f"Created {count} sample rides")
    return rides

async def create_sample_transactions(session: AsyncSession, rides: List[Ride]) -> List[Transaction]:
    """Create sample transactions for completed rides."""
    transactions = []
    completed_rides = [r for r in rides if r.status == "completed" and r.final_fare]
    
    gateways = ["razorpay", "paytm"]
    
    for ride in completed_rides:
        # 95% success rate for transactions
        status = "completed" if random.random() < 0.95 else "failed"
        
        transaction = Transaction(
            id=str(uuid.uuid4()),
            ride_id=ride.id,
            amount=ride.final_fare,
            gateway=random.choice(gateways),
            gateway_transaction_id=f"gw_{random.randint(100000, 999999)}",
            status=status,
            created_at=ride.completed_at or ride.created_at
        )
        
        session.add(transaction)
        transactions.append(transaction)
    
    await session.commit()
    print(f"Created {len(transactions)} sample transactions")
    return transactions

async def create_sample_payouts(session: AsyncSession, users: List[User], transactions: List[Transaction]):
    """Create sample driver payouts."""
    drivers = [u for u in users if u.user_type == "driver"]
    payouts = []
    
    for driver in drivers:
        # Get driver's completed transactions
        driver_transactions = [
            t for t in transactions 
            if t.status == "completed" and any(
                r.driver_id == driver.id for r in session.query(Ride).filter(Ride.id == t.ride_id)
            )
        ]
        
        if not driver_transactions:
            continue
        
        # Group transactions by week
        weeks = {}
        for txn in driver_transactions:
            week_start = txn.created_at - timedelta(days=txn.created_at.weekday())
            week_key = week_start.strftime("%Y-%W")
            
            if week_key not in weeks:
                weeks[week_key] = []
            weeks[week_key].append(txn)
        
        # Create payouts for each week
        for week_key, week_txns in weeks.items():
            total_amount = sum(t.amount for t in week_txns)
            driver_share = total_amount * 0.8  # 80% to driver
            
            payout = DriverPayout(
                id=str(uuid.uuid4()),
                driver_id=driver.id,
                amount=round(driver_share, 2),
                ride_count=len(week_txns),
                status=random.choice(["pending", "processed", "processed", "processed"]),  # Mostly processed
                created_at=max(t.created_at for t in week_txns) + timedelta(days=1)
            )
            
            session.add(payout)
            payouts.append(payout)
    
    await session.commit()
    print(f"Created {len(payouts)} sample payouts")
    return payouts

async def create_location_data(session: AsyncSession, users: List[User]):
    """Create location data in MongoDB (simulated)."""
    # This would typically insert into MongoDB
    # For now, we'll just print the count
    drivers = [u for u in users if u.user_type == "driver"]
    location_count = len(drivers) * random.randint(10, 50)  # Multiple location updates per driver
    print(f"Would create {location_count} location records in MongoDB")

async def main():
    """Main seeding function."""
    print("🌱 Starting database seeding...")
    print("=" * 50)
    
    try:
        # Get database session
        async for session in get_async_session():
            # Create users
            users = await create_users(session, count=50)
            
            # Create driver profiles
            drivers = [u for u in users if u.user_type == "driver"]
            await create_driver_profiles(session, drivers)
            
            # Create sample rides
            rides = await create_sample_rides(session, users, count=200)
            
            # Create transactions
            transactions = await create_sample_transactions(session, rides)
            
            # Create payouts
            await create_sample_payouts(session, users, transactions)
            
            # Create location data
            await create_location_data(session, users)
            
            print("=" * 50)
            print("✅ Database seeding completed successfully!")
            print(f"📊 Summary:")
            print(f"   - Users: {len(users)} ({len(drivers)} drivers)")
            print(f"   - Rides: {len(rides)}")
            print(f"   - Transactions: {len(transactions)}")
            print(f"   - Driver Profiles: {len(drivers)}")
            print("=" * 50)
            
            break  # Exit the async generator
            
    except Exception as e:
        print(f"❌ Error during seeding: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())