
from geopy.geocoders import GoogleV3

def geocode_address(api_key, user_address):
    # Initialize the geocoder with the API key
    geocoder = GoogleV3(api_key=api_key)

    # Geocode the user-provided address
    location = geocoder.geocode(
        query=user_address,
        exactly_one=True  # Return one result
    )

    if location:
        # Print the coordinates (latitude and longitude)
        print(f'Address: {location.address}')
        return location.latitude, location.longitude
    else:
        print(f'Location not found for the address: {user_address}')
        return None

# Replace with your Google Maps API Key
api_key = 'AIzaSyCp2utU1aL7MPxKMjCGJMuNpLpAKDnOie8'

user_address = ''    # Get address from web server

latitude, longitude = geocode_address(api_key, user_address) 

if latitude is not None and longitude is not None:
    print(f'Latitude: {latitude}')
    print(f'Longitude: {longitude}')
    
    # Send coordinates to the drone
