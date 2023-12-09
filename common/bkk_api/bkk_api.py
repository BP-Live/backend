import os
import json
import requests
import googlemaps
import pandas as pd
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
    location = location[0]
    """
    gmaps = googlemaps.Client(key=os.environ['NEXT_PUBLIC_MAP_API_KEY'])
    reverse_geocode_result = gmaps.reverse_geocode((float(lat), float(lon)))
    """
    return location # reverse_geocode_result

def find_shortest_route_time(lat1, lon1, lat2, lon2):
    print('Loc1_raw:', lat1, lon1)
    print('Loc2_raw:', lat2, lon2)

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
        directions_result = gmaps.directions((lat1, lon1), (lat2, lon2), mode="walking")

        print(directions_result)

        # Extract the distance from the directions result
        distance = directions_result[0]['legs'][0]['distance']['value']
    except Exception as e:
        print('Error:', e)
        distance = 0
    return distance, location1, location2

if __name__ == "__main__":
    premises_data = pd.read_csv(os.path.join(os.path.dirname(__file__), './../premises.csv'))
    # premises_data = premises_data[premises_data['2023nov_állapot'] == 'Üres']
    # premises_data.to_csv(os.path.join(os.path.dirname(__file__), 'premises_empty.csv'))
    
    unique_streets = []
    unique_street_names = []
    for index, row in premises_data.iterrows():
        street = row['Cím'].split('.')[0]
        street = street.replace('-', ' ').replace(',', ' ').replace('.', ' ').replace('(', ' ').replace(')', ' ')
        street = street.replace('1', '').replace('2', '').replace('3', '').replace('4', '').replace('5', '').replace('6', '').replace('7', '').replace('8', '').replace('9', '').replace('0', '')
        street = street.strip()

        if street not in unique_streets:
            unique_streets.append(street)
            unique_street_names.append(row['Cím'])

    rows = []

    for street_name in unique_street_names:
        geocode = geocode_location('Budapest, 8.kerület ' + street_name)
        lat, lng = (geocode[0]['geometry']['location']['lat'], geocode[0]['geometry']['location']['lng'])
        new_df_row = premises_data[premises_data['Cím'] == street_name].iloc[0]
        new_df_row['lat'] = lat
        new_df_row['lon'] = lng
        rows.append(new_df_row)
    
    df = pd.DataFrame(rows)
    df.to_csv(os.path.join(os.path.dirname(__file__), './../premises_geocoded.csv'))
