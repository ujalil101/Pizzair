from geopy.geocoders import GoogleV3

def geocode_address(api_key, user_address):
    # initialize the geocoder with the API key
    geocoder = GoogleV3(api_key=api_key)

    # geocode the user-provided address
    location = geocoder.geocode(
        query=user_address,
        exactly_one=True  # return one result
    )

    if location:
        # print the coordinates (latitude and longitude)
        print(f'Address: {location.address}')
        return location.latitude, location.longitude
    else:
        print(f'Location not found for the address: {user_address}')
        return None

# location.address is the variable that holds the detailed address the google maps finds, after user inputs their own address u can show this variable to confirm
# if this is the address user intended to input. I havent put it in myself because we dont need it outside of that, we are just going to send the coordinates.
