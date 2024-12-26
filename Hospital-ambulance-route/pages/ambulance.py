import requests
import networkx as nx
import numpy as np

# Google API keys
GEOCODING_API_KEY = 'AIzaSyCyJN5huOcigrXCnccBKZuefnlkEomb8ZQ'
PLACES_API_KEY = 'AIzaSyAZxtzTzIbzuF6JFr2RA1cT7DnfeDedusM'
DIRECTIONS_API_KEY = 'AIzaSyDlSuS-aM3GsXUy_sNlLivKkdL5h7jWAsc'

# Function to get coordinates from location name using Google Geocoding API
def get_coordinates(location):
    geocode_url = f"https://maps.googleapis.com/maps/api/geocode/json?address={location}&key={GEOCODING_API_KEY}"
    response = requests.get(geocode_url)
    geocode_result = response.json()
    if geocode_result['results']:
        lat = geocode_result['results'][0]['geometry']['location']['lat']
        lng = geocode_result['results'][0]['geometry']['location']['lng']
        return lat, lng
    return None, None

# Function to get real-time data using Google Places API
def get_real_time_locations(lat, lng, radius, place_type):
    places_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lng}&radius={radius}&type={place_type}&key={PLACES_API_KEY}"
    response = requests.get(places_url)
    places = response.json()['results']
    locations = [(place['name'], place['geometry']['location']['lat'], place['geometry']['location']['lng']) for place in places]
    return locations

# Function to calculate the driving distance using Google Maps Directions API
def get_driving_distance(source_lat, source_lng, dest_lat, dest_lng):
    directions_url = f"https://maps.googleapis.com/maps/api/directions/json?origin={source_lat},{source_lng}&destination={dest_lat},{dest_lng}&key={DIRECTIONS_API_KEY}"
    response = requests.get(directions_url)
    directions = response.json()
    if directions['routes']:
        distance = directions['routes'][0]['legs'][0]['distance']['value']  # distance in meters
        return distance / 1000  # convert to kilometers
    return None

# User input for current location and search radius
user_location = input("Enter your current location (e.g., Jogeshwari): ")
search_radius = input("Enter search radius in meters (e.g., 5000): ")

# Fetch coordinates for the user location
user_lat, user_lng = get_coordinates(user_location)
if user_lat is None or user_lng is None:
    print("Error: Unable to find coordinates for the specified location.")
    exit()

# Fetch real-time locations of nearby hospitals
real_time_hospitals = get_real_time_locations(user_lat, user_lng, search_radius, 'hospital')
if not real_time_hospitals:
    print("No hospitals found. Please try again with different inputs.")
    exit()

print("Real-time hospital locations:")
for loc in real_time_hospitals:
    print(f"- {loc[0]} (Lat: {loc[1]}, Lng: {loc[2]})")

# Fetch real-time locations of nearby ambulances
real_time_ambulances = get_real_time_locations(user_lat, user_lng, search_radius, 'ambulance')  # Assuming 'ambulance' is a place type
if not real_time_ambulances:
    print("No ambulances found. Please try again with different inputs.")
    exit()

print("\nReal-time ambulance locations:")
for loc in real_time_ambulances:
    print(f"- {loc[0]} (Lat: {loc[1]}, Lng: {loc[2]})")

# Extract node names, latitudes, and longitudes for hospitals and ambulances
hospital_nodes = [loc[0] for loc in real_time_hospitals]
ambulance_nodes = [loc[0] for loc in real_time_ambulances]
lat_lng_hospitals = {loc[0]: (loc[1], loc[2]) for loc in real_time_hospitals}
lat_lng_ambulances = {loc[0]: (loc[1], loc[2]) for loc in real_time_ambulances}

# Print the hospital and ambulance lists
print("\nHospitals:")
for node in hospital_nodes:
    print(f"- {node}")

print("\nAmbulances:")
for node in ambulance_nodes:
    print(f"- {node}")

# Ask user for destination hospital
end_location = input("Enter the hospital you wish to visit from the list above: ").strip()

# Check if the entered location is valid
if end_location not in lat_lng_hospitals:
    print("Error: Invalid hospital name. Please enter a hospital name from the list.")
    exit()

# Convert end location to coordinates
end_lat, end_lng = lat_lng_hospitals[end_location]

# Assign the nearest ambulance to the user's location
nearest_ambulance = None
shortest_distance = float('inf')
for ambulance, (amb_lat, amb_lng) in lat_lng_ambulances.items():
    distance = get_driving_distance(user_lat, user_lng, amb_lat, amb_lng)
    if distance is not None and distance < shortest_distance:
        nearest_ambulance = ambulance
        shortest_distance = distance

if nearest_ambulance is None:
    print("No available ambulances found.")
    exit()

ambulance_lat, ambulance_lng = lat_lng_ambulances[nearest_ambulance]
print(f"\nAssigned ambulance: {nearest_ambulance}")
print(f"Ambulance location: Lat: {ambulance_lat}, Lng: {ambulance_lng}")
print(f"Driving distance from ambulance to user location: {shortest_distance:.2f} kilometers")

# Create graph based on real driving distances between locations
G = nx.Graph()
for i in range(len(real_time_hospitals)):
    for j in range(i + 1, len(real_time_hospitals)):
        loc1, loc2 = real_time_hospitals[i], real_time_hospitals[j]
        dist = get_driving_distance(loc1[1], loc1[2], loc2[1], loc2[2])
        if dist is not None:
            G.add_edge(loc1[0], loc2[0], weight=dist)

# Add user location and nearest ambulance as nodes in the graph
G.add_node('User Location', pos=(user_lat, user_lng))
G.add_node(nearest_ambulance, pos=lat_lng_ambulances[nearest_ambulance])
for loc in real_time_hospitals:
    dist = get_driving_distance(user_lat, user_lng, loc[1], loc[2])
    if dist is not None:
        G.add_edge('User Location', loc[0], weight=dist)

dist_to_user = get_driving_distance(ambulance_lat, ambulance_lng, user_lat, user_lng)
if dist_to_user is not None:
    G.add_edge(nearest_ambulance, 'User Location', weight=dist_to_user)

# Shortest Path Calculation using Dijkstra's Algorithm
def shortest_path(graph, source, target):
    return nx.dijkstra_path(graph, source, target), nx.dijkstra_path_length(graph, source, target)

path, length = shortest_path(G, 'User Location', end_location)
print(f"\nShortest path from your location to {end_location} with assigned ambulance: {path}, Length: {length:.2f} kilometers")
