"""Models package for the ride-hailing platform."""

from app.models.user import User, DriverProfile, EmergencyContact, UserType, DriverStatus
from app.models.ride import Ride, RideStatus, PaymentStatus
from app.models.transaction import Transaction, DriverPayout, TransactionStatus, PaymentGateway, PayoutStatus
from app.models.verification import VerificationSession
from app.models.rating import Rating
from app.models.location import Location, LocationHistory, Coordinates

__all__ = [
    # User models
    'User',
    'DriverProfile',
    'EmergencyContact',
    'UserType',
    'DriverStatus',
    # Ride models
    'Ride',
    'RideStatus',
    'PaymentStatus',
    # Transaction models
    'Transaction',
    'DriverPayout',
    'TransactionStatus',
    'PaymentGateway',
    'PayoutStatus',
    # Verification models
    'VerificationSession',
    # Rating models
    'Rating',
    # Location models
    'Location',
    'LocationHistory',
    'Coordinates',
]
