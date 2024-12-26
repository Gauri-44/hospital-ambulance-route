import requests
import networkx as nx
import numpy as np
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

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

# Combine data into a DataFrame
hospital_data = pd.DataFrame(real_time_hospitals, columns=['Name', 'Latitude', 'Longitude'])
ambulance_data = pd.DataFrame(real_time_ambulances, columns=['Name', 'Latitude', 'Longitude'])
hospital_data['Type'] = 'Hospital'
ambulance_data['Type'] = 'Ambulance'
combined_data = pd.concat([hospital_data, ambulance_data])

# K-Means Clustering
def k_means_clustering(coordinates, n_clusters):
    kmeans = KMeans(n_clusters=n_clusters, random_state=0).fit(coordinates)
    return kmeans.labels_, kmeans.cluster_centers_

# Combine hospital and ambulance coordinates for clustering
hospital_coords = hospital_data[['Latitude', 'Longitude']].values
ambulance_coords = ambulance_data[['Latitude', 'Longitude']].values
all_coords = np.vstack((hospital_coords, ambulance_coords))

# Perform clustering
n_clusters = 3  # Example: Number of clusters
labels, cluster_centers = k_means_clustering(all_coords, n_clusters)
combined_data['Cluster'] = labels

# Print cluster assignments
print("\nCluster Assignments:")
for i, label in enumerate(labels):
    if i < len(hospital_nodes):
        print(f"Hospital: {hospital_nodes[i]} -> Cluster {label}")
    else:
        print(f"Ambulance: {ambulance_nodes[i - len(hospital_nodes)]} -> Cluster {label}")

# Print cluster centers
print("\nCluster Centers:")
for center in cluster_centers:
    print(center)

# Plot Clustering Results
plt.figure(figsize=(10, 7))
sns.scatterplot(x='Longitude', y='Latitude', hue='Cluster', style='Type', s=100, data=combined_data, palette='viridis', markers=["o", "s"])
plt.scatter(cluster_centers[:, 1], cluster_centers[:, 0], c='red', marker='x', s=100, label='Centers')
plt.title('K-Means Clustering of Hospitals and Ambulances')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.legend()
plt.show()

# Additional EDA

# Histograms for Latitude and Longitude
plt.figure(figsize=(14, 6))
plt.subplot(1, 2, 1)
sns.histplot(combined_data['Latitude'], kde=True, color='blue')
plt.title('Latitude Distribution')

plt.subplot(1, 2, 2)
sns.histplot(combined_data['Longitude'], kde=True, color='green')
plt.title('Longitude Distribution')
plt.show()

# Scatter Plot with Annotations
plt.figure(figsize=(10, 7))
sns.scatterplot(x='Longitude', y='Latitude', hue='Type', data=combined_data, palette='coolwarm', s=100)
for line in range(0, combined_data.shape[0]):
    plt.text(combined_data.Longitude.iloc[line], combined_data.Latitude.iloc[line], combined_data.Name.iloc[line], horizontalalignment='left', size='small', color='black', weight='semibold')
plt.title('Scatter Plot of Locations with Annotations')
plt.xlabel('Longitude')
plt.ylabel('Latitude')
plt.show()

# Pair Plot
sns.pairplot(combined_data, hue='Type', palette='coolwarm')
plt.suptitle('Pair Plot of Locations', y=1.02)
plt.show()

# Heatmap
plt.figure(figsize=(10, 7))
corr = combined_data[['Latitude', 'Longitude']].corr()
sns.heatmap(corr, annot=True, cmap='coolwarm', linewidths=0.5)
plt.title('Correlation Heatmap')
plt.show()
