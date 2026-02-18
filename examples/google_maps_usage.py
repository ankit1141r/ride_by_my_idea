"""
Example usage of Google Maps integration in Location Service.

This script demonstrates how to use the address search and route calculation
features integrated with Google Maps API.

Requirements: 2.6, 8.3, 8.6
"""
import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from app.services.location_service import LocationService
from app.config import settings


async def main():
    """Demonstrate Google Maps integration features."""
    
    # Initialize MongoDB client
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client[settings.mongodb_db]
    
    # Create location service
    location_service = LocationService(db)
    
    print("=" * 60)
    print("Google Maps Integration Demo")
    print("=" * 60)
    
    # Example 1: Address Search
    print("\n1. Address Search")
    print("-" * 60)
    
    search_query = "Rajwada"
    print(f"Searching for: {search_query}")
    
    try:
        results = location_service.search_address(search_query, limit=3)
        
        if results:
            print(f"\nFound {len(results)} results:")
            for i, result in enumerate(results, 1):
                print(f"\n  Result {i}:")
                print(f"    Address: {result['address']}")
                print(f"    Latitude: {result['latitude']}")
                print(f"    Longitude: {result['longitude']}")
                print(f"    Place ID: {result['place_id']}")
        else:
            print("No results found within service area")
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    
    # Example 2: Route Calculation
    print("\n\n2. Route Calculation")
    print("-" * 60)
    
    # Example coordinates within Indore
    origin_lat, origin_lng = 22.7196, 75.8577  # Rajwada area
    dest_lat, dest_lng = 22.7532, 75.8937      # Vijay Nagar area
    
    print(f"Origin: ({origin_lat}, {origin_lng})")
    print(f"Destination: ({dest_lat}, {dest_lng})")
    
    try:
        route = location_service.calculate_route(
            origin_lat, origin_lng,
            dest_lat, dest_lng
        )
        
        if route:
            print("\nRoute Details:")
            print(f"  Distance: {route['distance_km']} km")
            print(f"  Duration: {route['duration_minutes']} minutes")
            print(f"  Waypoints: {len(route['waypoints'])} points")
            print(f"  Polyline: {route['polyline'][:50]}...")  # Show first 50 chars
            
            print("\n  Bounds:")
            print(f"    Northeast: ({route['bounds']['northeast']['latitude']}, "
                  f"{route['bounds']['northeast']['longitude']})")
            print(f"    Southwest: ({route['bounds']['southwest']['latitude']}, "
                  f"{route['bounds']['southwest']['longitude']})")
            
            print("\n  First 3 waypoints:")
            for i, waypoint in enumerate(route['waypoints'][:3], 1):
                print(f"    {i}. ({waypoint['latitude']}, {waypoint['longitude']})")
        else:
            print("No route found")
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    
    # Example 3: Boundary Validation
    print("\n\n3. Boundary Validation")
    print("-" * 60)
    
    test_locations = [
        ("Inside Indore", 22.7196, 75.8577),
        ("Outside Indore", 23.0, 76.0)
    ]
    
    for name, lat, lng in test_locations:
        is_valid = location_service.is_within_service_area(lat, lng)
        print(f"{name} ({lat}, {lng}): {'✓ Valid' if is_valid else '✗ Invalid'}")
    
    print("\n" + "=" * 60)
    print("Demo Complete")
    print("=" * 60)
    
    # Close MongoDB connection
    client.close()


if __name__ == "__main__":
    asyncio.run(main())
