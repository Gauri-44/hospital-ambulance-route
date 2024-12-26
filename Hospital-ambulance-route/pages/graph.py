import requests
import networkx as nx
import numpy as np
from sklearn.cluster import KMeans
from sklearn.linear_model import LinearRegression

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

# Function to get real-time hospital data using Google Places API
def get_real_time_locations(lat, lng, radius):
    places_url = f"https://maps.googleapis.com/maps/api/place/nearbysearch/json?location={lat},{lng}&radius={radius}&type=hospital&key={PLACES_API_KEY}"
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
real_time_locations = get_real_time_locations(user_lat, user_lng, search_radius)
if not real_time_locations:
    print("No locations found. Please try again with different inputs.")
    exit()

print("Real-time locations:")
for loc in real_time_locations:
    print(f"- {loc[0]} (Lat: {loc[1]}, Lng: {loc[2]})")

# Extract node names, latitudes, and longitudes
nodes = [loc[0] for loc in real_time_locations]
lat_lng = {loc[0]: (loc[1], loc[2]) for loc in real_time_locations}

# Print the hospital list in a more readable format
print("\nHospitals:")
for node in nodes:
    print(f"- {node}")

# Ask user for destination hospital and handle potential extra spaces
end_location = input("Enter the hospital you wish to visit from the list above: ").strip()

# Check if the entered location is valid
if end_location not in lat_lng:
    print("Error: Invalid hospital name. Please enter a hospital name from the list.")
    exit()

# Convert end location to coordinates
end_lat, end_lng = lat_lng[end_location]

# Create graph based on real driving distances between locations
G = nx.Graph()
for i in range(len(real_time_locations)):
    for j in range(i + 1, len(real_time_locations)):
        loc1, loc2 = real_time_locations[i], real_time_locations[j]
        dist = get_driving_distance(loc1[1], loc1[2], loc2[1], loc2[2])
        if dist is not None:
            G.add_edge(loc1[0], loc2[0], weight=dist)

# Add user location as a node in the graph
G.add_node('User Location', pos=(user_lat, user_lng))
for loc in real_time_locations:
    dist = get_driving_distance(user_lat, user_lng, loc[1], loc[2])
    if dist is not None:
        G.add_edge('User Location', loc[0], weight=dist)

# Shortest Path Calculation using Dijkstra's Algorithm
def shortest_path(graph, source, target):
    return nx.dijkstra_path(graph, source, target), nx.dijkstra_path_length(graph, source, target)

path, length = shortest_path(G, 'User Location', end_location)
print(f"Shortest path from your location to {end_location}: {path}, Length: {length:.2f} kilometers")

