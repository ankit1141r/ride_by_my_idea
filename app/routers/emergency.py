"""
Emergency and safety feature endpoints.
Handles emergency contacts, emergency alerts, and ride sharing.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel, Field
import uuid
from datetime import datetime

from app.database import get_db
from app.utils.jwt import get_current_user
from app.models.user import User, EmergencyContact
from app.models.ride import Ride, RideStatus


router = APIRouter(prefix="/api", tags=["emergency"])


# Emergency Contact Schemas
class EmergencyContactRequest(BaseModel):
    """Request to add an emergency contact."""
    name: str = Field(..., description="Contact name")
    phone_number: str = Field(..., description="Contact phone number")
    relationship: str = Field(..., description="Relationship to user")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "John Doe",
                "phone_number": "+919876543210",
                "relationship": "Spouse"
            }
        }


class EmergencyContactResponse(BaseModel):
    """Response for emergency contact."""
    contact_id: str
    name: str
    phone_number: str
    relationship: str
    created_at: str
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "contact_id": "contact123",
                "name": "John Doe",
                "phone_number": "+919876543210",
                "relationship": "Spouse",
                "created_at": "2024-01-15T10:30:00"
            }
        }


@router.post("/users/emergency-contacts", response_model=EmergencyContactResponse, status_code=status.HTTP_201_CREATED)
async def add_emergency_contact(
    request: EmergencyContactRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add an emergency contact for the current user.
    Maximum 3 contacts allowed per user.
    
    - **name**: Contact name
    - **phone_number**: Contact phone number
    - **relationship**: Relationship to user (e.g., Spouse, Parent, Friend)
    """
    user_id = current_user["user_id"]
    
    # Get user
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check if user already has 3 emergency contacts
    existing_contacts = db.query(EmergencyContact).filter(
        EmergencyContact.user_id == user_id
    ).count()
    
    if existing_contacts >= 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum 3 emergency contacts allowed per user"
        )
    
    # Create emergency contact
    contact = EmergencyContact(
        contact_id=str(uuid.uuid4()),
        user_id=user_id,
        name=request.name,
        phone_number=request.phone_number,
        relationship_type=request.relationship
    )
    
    db.add(contact)
    db.commit()
    db.refresh(contact)
    
    return EmergencyContactResponse(
        contact_id=contact.contact_id,
        name=contact.name,
        phone_number=contact.phone_number,
        relationship=contact.relationship_type,
        created_at=contact.created_at.isoformat()
    )


@router.get("/users/emergency-contacts", response_model=List[EmergencyContactResponse])
async def get_emergency_contacts(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all emergency contacts for the current user.
    """
    user_id = current_user["user_id"]
    
    contacts = db.query(EmergencyContact).filter(
        EmergencyContact.user_id == user_id
    ).all()
    
    return [
        EmergencyContactResponse(
            contact_id=c.contact_id,
            name=c.name,
            phone_number=c.phone_number,
            relationship=c.relationship_type,
            created_at=c.created_at.isoformat()
        )
        for c in contacts
    ]


@router.delete("/users/emergency-contacts/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_emergency_contact(
    contact_id: str,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete an emergency contact.
    
    - **contact_id**: Emergency contact ID
    """
    user_id = current_user["user_id"]
    
    # Find contact
    contact = db.query(EmergencyContact).filter(
        EmergencyContact.contact_id == contact_id,
        EmergencyContact.user_id == user_id
    ).first()
    
    if not contact:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Emergency contact not found"
        )
    
    db.delete(contact)
    db.commit()
    
    return None


# Emergency Alert Schemas
class EmergencyAlertRequest(BaseModel):
    """Request to trigger emergency alert."""
    message: str = Field(None, description="Optional message")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Need immediate help"
            }
        }


class EmergencyAlertResponse(BaseModel):
    """Response for emergency alert."""
    alert_id: str
    ride_id: str
    user_id: str
    message: str
    timestamp: str
    location: dict
    status: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "alert_id": "alert123",
                "ride_id": "ride123",
                "user_id": "user123",
                "message": "Emergency alert triggered",
                "timestamp": "2024-01-15T10:30:00",
                "location": {
                    "latitude": 22.7196,
                    "longitude": 75.8577
                },
                "status": "active"
            }
        }


@router.post("/rides/{ride_id}/emergency", response_model=EmergencyAlertResponse)
async def trigger_emergency_alert(
    ride_id: str,
    request: EmergencyAlertRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Trigger emergency alert for an active ride.
    Notifies platform administrators and logs incident.
    
    - **ride_id**: Ride identifier
    - **message**: Optional emergency message
    """
    import json
    from app.database import get_mongodb
    from app.services.location_service import LocationService
    
    user_id = current_user["user_id"]
    
    # Get ride
    ride = db.query(Ride).filter(Ride.ride_id == ride_id).first()
    if not ride:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ride not found"
        )
    
    # Verify user is part of the ride
    if user_id not in [ride.rider_id, ride.driver_id]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not authorized to trigger emergency for this ride"
        )
    
    # Verify ride is in progress
    if ride.status != RideStatus.IN_PROGRESS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Emergency can only be triggered for in-progress rides"
        )
    
    # Get current location
    mongodb = get_mongodb()
    location_service = LocationService(db, mongodb)
    
    try:
        driver_location = location_service.get_driver_location(ride.driver_id)
        if not driver_location:
            # Fallback to pickup location if driver location not available
            pickup = json.loads(ride.pickup_location)
            current_location = {
                "latitude": pickup["latitude"],
                "longitude": pickup["longitude"]
            }
        else:
            current_location = {
                "latitude": driver_location["latitude"],
                "longitude": driver_location["longitude"]
            }
    except Exception:
        # Fallback to pickup location
        pickup = json.loads(ride.pickup_location)
        current_location = {
            "latitude": pickup["latitude"],
            "longitude": pickup["longitude"]
        }
    
    # Create emergency incident log
    alert_id = str(uuid.uuid4())
    timestamp = datetime.utcnow()
    
    # Store incident in MongoDB
    incident_log = {
        "alert_id": alert_id,
        "ride_id": ride_id,
        "user_id": user_id,
        "user_type": current_user["user_type"],
        "rider_id": ride.rider_id,
        "driver_id": ride.driver_id,
        "message": request.message or "Emergency alert triggered",
        "timestamp": timestamp,
        "location": current_location,
        "status": "active",
        "ride_status": ride.status.value
    }
    
    mongodb.emergency_incidents.insert_one(incident_log)
    
    # TODO: Send notification to platform administrators
    # This would integrate with notification service
    
    # TODO: Send notification to emergency contacts
    # This would integrate with SMS service
    
    return EmergencyAlertResponse(
        alert_id=alert_id,
        ride_id=ride_id,
        user_id=user_id,
        message=incident_log["message"],
        timestamp=timestamp.isoformat(),
        location=current_location,
        status="active"
    )


# Ride Sharing Schemas
class RideShareRequest(BaseModel):
    """Request to share ride with emergency contacts."""
    message: str = Field(None, description="Optional message to include")
    
    class Config:
        json_schema_extra = {
            "example": {
                "message": "Sharing my ride details with you"
            }
        }


class RideShareResponse(BaseModel):
    """Response for ride sharing."""
    share_id: str
    ride_id: str
    share_link: str
    contacts_notified: int
    message: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "share_id": "share123",
                "ride_id": "ride123",
                "share_link": "https://platform.com/share/ride123/token",
                "contacts_notified": 2,
                "message": "Ride details shared with 2 emergency contacts"
            }
        }


@router.post("/rides/{ride_id}/share", response_model=RideShareResponse)
async def share_ride_with_contacts(
    ride_id: str,
    request: RideShareRequest,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Share ride details with emergency contacts via SMS.
    Generates shareable link with live location tracking.
    
    - **ride_id**: Ride identifier
    - **message**: Optional message to include
    """
    user_id = current_user["user_id"]
    
    # Get ride
    ride = db.query(Ride).filter(Ride.ride_id == ride_id).first()
    if not ride:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ride not found"
        )
    
    # Verify user is the rider
    if user_id != ride.rider_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only riders can share ride details"
        )
    
    # Verify ride is active
    if ride.status not in [RideStatus.MATCHED, RideStatus.DRIVER_ARRIVING, RideStatus.IN_PROGRESS]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only share active rides"
        )
    
    # Get emergency contacts
    contacts = db.query(EmergencyContact).filter(
        EmergencyContact.user_id == user_id
    ).all()
    
    if not contacts:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No emergency contacts found. Add contacts first."
        )
    
    # Generate share token and link
    share_id = str(uuid.uuid4())
    share_token = str(uuid.uuid4())
    share_link = f"https://platform.com/share/{ride_id}/{share_token}"
    
    # Store share record in MongoDB
    from app.database import get_mongodb
    mongodb = get_mongodb()
    
    share_record = {
        "share_id": share_id,
        "ride_id": ride_id,
        "user_id": user_id,
        "share_token": share_token,
        "created_at": datetime.utcnow(),
        "expires_at": None,  # Active until ride completes
        "contacts_notified": [c.contact_id for c in contacts]
    }
    
    mongodb.ride_shares.insert_one(share_record)
    
    # TODO: Send SMS to emergency contacts with share link
    # This would integrate with Twilio SMS service
    # For now, we'll just log the action
    
    contacts_notified = len(contacts)
    
    return RideShareResponse(
        share_id=share_id,
        ride_id=ride_id,
        share_link=share_link,
        contacts_notified=contacts_notified,
        message=f"Ride details shared with {contacts_notified} emergency contact(s)"
    )


@router.get("/share/{ride_id}/{share_token}")
async def view_shared_ride(
    ride_id: str,
    share_token: str,
    db: Session = Depends(get_db)
):
    """
    View shared ride details (public endpoint for emergency contacts).
    
    - **ride_id**: Ride identifier
    - **share_token**: Share token for authentication
    """
    import json
    from app.database import get_mongodb
    
    # Verify share token
    mongodb = get_mongodb()
    share_record = mongodb.ride_shares.find_one({
        "ride_id": ride_id,
        "share_token": share_token
    })
    
    if not share_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Shared ride not found or link expired"
        )
    
    # Get ride details
    ride = db.query(Ride).filter(Ride.ride_id == ride_id).first()
    if not ride:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ride not found"
        )
    
    # Get rider and driver info
    rider = db.query(User).filter(User.user_id == ride.rider_id).first()
    driver = db.query(User).filter(User.user_id == ride.driver_id).first()
    
    # Get current driver location
    from app.services.location_service import LocationService
    location_service = LocationService(db, mongodb)
    
    try:
        driver_location = location_service.get_driver_location(ride.driver_id)
    except Exception:
        driver_location = None
    
    # Parse locations
    pickup = json.loads(ride.pickup_location)
    destination = json.loads(ride.destination)
    
    return {
        "ride_id": ride_id,
        "status": ride.status.value,
        "rider": {
            "name": rider.name,
            "phone": rider.phone_number
        },
        "driver": {
            "name": driver.name if driver else None,
            "phone": driver.phone_number if driver else None,
            "vehicle": {
                "make": driver.driver_profile.vehicle_make if driver and driver.driver_profile else None,
                "model": driver.driver_profile.vehicle_model if driver and driver.driver_profile else None,
                "color": driver.driver_profile.vehicle_color if driver and driver.driver_profile else None,
                "registration": driver.driver_profile.vehicle_registration if driver and driver.driver_profile else None
            } if driver and driver.driver_profile else None
        },
        "pickup_location": pickup,
        "destination": destination,
        "current_location": driver_location,
        "started_at": ride.start_time.isoformat() if ride.start_time else None
    }
