import pandas as pd

import os

from .bkk_api import bkk_api

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

    time1, _, loc1 = bkk_api.find_shortest_route_time(lat, lng, n1lat, n1lon)
    time2, _, loc2 = bkk_api.find_shortest_route_time(lat, lng, n2lat, n2lon)
    time3, _, loc3 = bkk_api.find_shortest_route_time(lat, lng, n3lat, n3lon)

    json_data = {
        "competitors": [
            {"lat": n1lat, "lng": n1lon, "distance": time1, "location": loc1},
            {"lat": n2lat, "lng": n2lon, "distance": time2, "location": loc2},
            {"lat": n3lat, "lng": n3lon, "distance": time3, "location": loc3},
        ]
    }
    
    return json_data

def find_open_premises(lat, lng):
    premises_data = pd.read_csv(os.path.join(os.path.dirname(__file__), 'premises_geocoded.csv'))
    # premises_data = premises_data[premises_data['2023nov_állapot'] == 'Üres']
    # premises_data.to_csv(os.path.join(os.path.dirname(__file__), 'premises_empty.csv'))

    k_nearest = get_k_nearest(premises_data, lat, lng, k=5)

    json_data = {
        "premises": [
            {"lat": k_nearest.iloc[0]["lat"], "lng": k_nearest.iloc[0]["lon"], "address": k_nearest.iloc[0]["Cím"], "area": k_nearest.iloc[0]["Terület"]},
            {"lat": k_nearest.iloc[1]["lat"], "lng": k_nearest.iloc[1]["lon"], "address": k_nearest.iloc[1]["Cím"], "area": k_nearest.iloc[1]["Terület"]},
            {"lat": k_nearest.iloc[2]["lat"], "lng": k_nearest.iloc[2]["lon"], "address": k_nearest.iloc[2]["Cím"], "area": k_nearest.iloc[2]["Terület"]},
            {"lat": k_nearest.iloc[3]["lat"], "lng": k_nearest.iloc[3]["lon"], "address": k_nearest.iloc[3]["Cím"], "area": k_nearest.iloc[3]["Terület"]},
            {"lat": k_nearest.iloc[4]["lat"], "lng": k_nearest.iloc[4]["lon"], "address": k_nearest.iloc[4]["Cím"], "area": k_nearest.iloc[4]["Terület"]},    
        ]
    }

    return json_data