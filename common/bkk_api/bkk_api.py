import os
import json
import requests
import googlemaps

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
    # Request data from BKK API
    gmaps = googlemaps.Client(key=os.environ['NEXT_PUBLIC_MAP_API_KEY'])
    geocode_result = gmaps.geocode(location)
    return geocode_result

def find_shortest_route_time(lat1, lon1, lat2, lon2):
    # Request data from Google Maps API
    gmaps = googlemaps.Client(key=os.environ['NEXT_PUBLIC_MAP_API_KEY'])
    directions_result = gmaps.directions((lat1, lon1), (lat2, lon2))
    return directions_result[0]['legs'][0]['duration']['value']