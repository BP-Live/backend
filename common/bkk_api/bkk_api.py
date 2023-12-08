import os
import json
import requests

import gtfs_realtime_pb2

with open("data.pb", "wb") as f:
    f.write(response.content)

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
