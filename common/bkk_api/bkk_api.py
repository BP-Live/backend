import os
import json
import requests
import googlemaps
from geopy.geocoders import Nominatim

from . import gtfs_realtime_pb2

def parse_vehicle_positions(protobuf_data):
    # Create an instance of FeedMessage
    feed = gtfs_realtime_pb2.FeedMessage()

    # Parse the protobuf data
    feed.ParseFromString(protobuf_data)

    # Extract vehicle positions and names
    vehicle_positions = []
    for entity in feed.entity:
        if entity.HasField('vehicle'):
            vehicle_data = {
                'id': entity.id,
                'latitude': entity.vehicle.position.latitude if entity.vehicle.position else None,
                'longitude': entity.vehicle.position.longitude if entity.vehicle.position else None,
                'vehicle_label': entity.vehicle.vehicle.label if entity.vehicle.vehicle else None
            }
            vehicle_positions.append(vehicle_data)

    return vehicle_positions

def request_data():
    # Request data from BKK API
    url = f"https://go.bkk.hu/api/query/v1/ws/gtfs-rt/full/VehiclePositions.pb?key={os.environ['BKK_API']}"
    response = requests.get(url)
    return response.content

def get_vehicle_positions():
    # Get vehicle positions
    protobuf_data = request_data()
    # Parse data to json
    vehicle_positions = parse_vehicle_positions(protobuf_data)
    return vehicle_positions

def geocode_location(location):
    # Request data from Google Maps API
    gmaps = googlemaps.Client(key=os.environ['NEXT_PUBLIC_MAP_API_KEY'])
    geocode_result = gmaps.geocode(address=location)
    return geocode_result

def reverse_geocode(lat, lon):
    # Request data from 
    
    geolocator = Nominatim(user_agent="my-app")
    location = geolocator.reverse(f"{lat}, {lon}")
    """
    gmaps = googlemaps.Client(key=os.environ['NEXT_PUBLIC_MAP_API_KEY'])
    reverse_geocode_result = gmaps.reverse_geocode((float(lat), float(lon)))
    """
    return location # reverse_geocode_result

def find_shortest_route_time(lat1, lon1, lat2, lon2):
    # Request data from Google Maps API
    try:
        location1 = reverse_geocode(lat1, lon1) # [0]['formatted_address']
    except:
        location1 = str(lat1) + "," + str(lon1)

    try:
        location2 = reverse_geocode(lat2, lon2) # [0]['formatted_address']
    except:
        location2 = str(lat2) + "," + str(lon2)

    print('Loc1:', location1)
    print('Loc2:', location2)

    gmaps = googlemaps.Client(key=os.environ['NEXT_PUBLIC_MAP_API_KEY'])

    try:
        directions_result = gmaps.directions(location1, location2, mode="walking")

        print(directions_result)

        # Extract the distance from the directions result
        distance = directions_result[0]['legs'][0]['distance']['value']
    except Exception as e:
        print('Error:', e)
        distance = 0
    return distance

if __name__ == "__main__":
    print(find_shortest_route_time(47.497913, 19.040236, 47.49723, 19.04026))