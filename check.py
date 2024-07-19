import phonenumbers
from phonenumbers import geocoder, carrier
from opencage.geocoder import OpenCageGeocode
import folium

# OpenCage API key
Key = "74307ce19f734723baf61058640390de"

# Function to retrieve geolocation based on phone number
def get_phone_number_location(number):
    try:
        # Parse the phone number
        check_number = phonenumbers.parse(number, None)

        # Get country information
        number_location = geocoder.description_for_number(check_number, "en")
        print("Country:", number_location)

        # Get carrier information
        service_provider = carrier.name_for_number(check_number, "en")
        print("Service Provider:", service_provider)

        # Initialize OpenCage geocoder
        geocoder_api = OpenCageGeocode(Key)

        # Query for geolocation based on country name
        query = number_location
        results = geocoder_api.geocode(query)

        if results:
            # Extract latitude and longitude
            lat = results[0]['geometry']['lat']
            lng = results[0]['geometry']['lng']
            print("Latitude:", lat)
            print("Longitude:", lng)

            # Create map using folium
            map_location = folium.Map(location=[lat, lng], zoom_start=9)
            folium.Marker([lat, lng], popup=f"{number_location} - {service_provider}").add_to(map_location)
            map_location.save("phone_location.html")
            print("Map saved as phone_location.html")
        else:
            print("No geolocation data found for", query)
    
    except phonenumbers.phonenumberutil.NumberParseException as e:
        print("Invalid phone number:", e)

# Example usage
if __name__ == "__main__":
    phone_number = input("Enter phone number with country code: ")
    get_phone_number_location(phone_number)


