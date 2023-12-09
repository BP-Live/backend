import pandas as pd

from .bkk_api import bkk_api

import os

def get_distance(lat1, lon1, lat2, lon2):
    return ((lat1-lat2)**2 + (lon1-lon2)**2)**0.5

def get_k_nearest(data, lat, lon, k=3):
    data_copy = data.copy()
    data_copy['distance'] = data_copy.apply(lambda x: get_distance(lat, lon, x['lat'], x['lon']), axis=1)
    return data_copy.sort_values(by=['distance']).head(k)

def find_competitors(business_type, lat, lng):
    dataset = pd.read_csv(os.path.join(os.path.dirname(__file__), 'pois.csv'))
    business_data = dataset[dataset['property_type'] == business_type]
    k_nearest = get_k_nearest(business_data, lat, lng)

    n1lat, n1lon = k_nearest.iloc[0]["lat"], k_nearest.iloc[0]["lon"]
    n2lat, n2lon = k_nearest.iloc[1]["lat"], k_nearest.iloc[1]["lon"]
    n3lat, n3lon = k_nearest.iloc[2]["lat"], k_nearest.iloc[2]["lon"]

    time1 = bkk_api.find_shortest_route_time(lat, lng, n1lat, n1lon)
    time2 = bkk_api.find_shortest_route_time(lat, lng, n2lat, n2lon)
    time3 = bkk_api.find_shortest_route_time(lat, lng, n3lat, n3lon)

    json_data = {
        "competitors": [
            {"lat": n1lat, "lng": n1lon, "distance": time1},
            {"lat": n2lat, "lng": n2lon, "distance": time2},
            {"lat": n3lat, "lng": n3lon, "distance": time3},
        ]
    }
    
    return json_data
