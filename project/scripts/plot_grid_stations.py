#!/usr/bin/env python3
"""
Visualize ECMWF 0.25° grid points vs actual station locations.
Shows spatial offset between model grid and observation points.
"""

import json
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from pathlib import Path

# Load station data
STATION_FILE = Path("stations.json")  # Adjust path to your JSON file
with open(STATION_FILE, "r") as f:
    data = json.load(f)

# Extract all stations
stations = []
for category in ["onshore", "coastal", "offshore"]:
    for station in data["stations"][category]:
        stations.append({
            "name": station["name"],
            "lat": station["latitude"],
            "lon": station["longitude"],
            "type": category
        })

# Define Irish domain bounds
LAT_MIN, LAT_MAX = 50.0, 56.0
LON_MIN, LON_MAX = -16.5, -5.0

# Generate 0.25° grid
RESOLUTION = 0.25
lats = np.arange(LAT_MIN, LAT_MAX + RESOLUTION, RESOLUTION)
lons = np.arange(LON_MIN, LON_MAX + RESOLUTION, RESOLUTION)
grid_lons, grid_lats = np.meshgrid(lons, lats)

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance in km between two lat/lon points"""
    R = 6371  # Earth radius in km
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(a))
    return R * c

def find_nearest_grid_point(lat, lon, grid_lats, grid_lons):
    """Find nearest grid point to a station"""
    distances = haversine_distance(lat, lon, grid_lats, grid_lons)
    idx = np.unravel_index(np.argmin(distances), distances.shape)
    nearest_lat = grid_lats[idx]
    nearest_lon = grid_lons[idx]
    distance = distances[idx]
    return nearest_lat, nearest_lon, distance

# Create figure
fig = plt.figure(figsize=(12, 10))
ax = plt.axes(projection=ccrs.PlateCarree())
ax.set_extent([LON_MIN, LON_MAX, LAT_MIN, LAT_MAX], crs=ccrs.PlateCarree())

# Add map features
ax.add_feature(cfeature.LAND, facecolor='lightgray')
ax.add_feature(cfeature.OCEAN, facecolor='lightblue')
ax.add_feature(cfeature.COASTLINE, linewidth=0.8)
ax.add_feature(cfeature.BORDERS, linestyle=':', linewidth=0.5)
ax.gridlines(draw_labels=True, linewidth=0.5, alpha=0.5)

# Plot grid points
ax.scatter(grid_lons, grid_lats, c='red', s=5, alpha=0.3, 
           label='ECMWF 0.25° grid', transform=ccrs.PlateCarree(), zorder=1)

# Color map for station types
colors = {"onshore": "green", "coastal": "orange", "offshore": "blue"}

# Plot stations and connections to nearest grid point
for station in stations:
    lat = station["lat"]
    lon = station["lon"]
    name = station["name"]
    stype = station["type"]
    
    # Find nearest grid point
    nearest_lat, nearest_lon, distance = find_nearest_grid_point(
        lat, lon, grid_lats, grid_lons
    )
    
    # Plot nearest grid point (highlighted)
    ax.scatter(nearest_lon, nearest_lat, c='darkred', s=80, marker='s', 
               edgecolors='black', linewidth=1.5,
               transform=ccrs.PlateCarree(), zorder=2)
    
    # Plot connection line (thicker and more visible)
    ax.plot([lon, nearest_lon], [lat, nearest_lat], 
            color='red', linestyle='--', linewidth=2.5, alpha=0.8,
            transform=ccrs.PlateCarree(), zorder=2)
    
    # Plot station
    ax.scatter(lon, lat, c=colors[stype], s=100, marker='o', 
               edgecolors='black', linewidth=1.5,
               transform=ccrs.PlateCarree(), zorder=3)
    
    # Add station label
    ax.text(lon, lat + 0.15, name, fontsize=9, ha='center', 
            fontweight='bold',
            transform=ccrs.PlateCarree(), zorder=4,
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    
    # Add distance label at midpoint
    mid_lat = (lat + nearest_lat) / 2
    mid_lon = (lon + nearest_lon) / 2
    ax.text(mid_lon, mid_lat, f'{distance:.1f} km', fontsize=8, 
            ha='center', style='italic', color='darkred', fontweight='bold',
            transform=ccrs.PlateCarree(), zorder=4,
            bbox=dict(boxstyle='round,pad=0.2', facecolor='yellow', alpha=0.7))

# Create legend
from matplotlib.lines import Line2D
legend_elements = [
    Line2D([0], [0], marker='o', color='w', label='All grid points (0.25°)',
           markerfacecolor='red', markersize=6, alpha=0.5),
    Line2D([0], [0], marker='s', color='w', label='Nearest grid point to station',
           markerfacecolor='darkred', markersize=8, markeredgecolor='black'),
    Line2D([0], [0], marker='o', color='w', label='Onshore stations',
           markerfacecolor='green', markersize=10, markeredgecolor='black'),
    Line2D([0], [0], marker='o', color='w', label='Coastal stations',
           markerfacecolor='orange', markersize=10, markeredgecolor='black'),
    Line2D([0], [0], marker='o', color='w', label='Offshore buoys',
           markerfacecolor='blue', markersize=10, markeredgecolor='black'),
    Line2D([0], [0], color='red', linestyle='--', linewidth=2, label='Distance to nearest grid point')
]
ax.legend(handles=legend_elements, loc='upper left', fontsize=9)

plt.title('ECMWF 0.25° Grid vs Irish Station Locations\nSpatial Offset Analysis', 
          fontsize=14, fontweight='bold')

plt.tight_layout()
plt.savefig('grid_station_map.png', dpi=300, bbox_inches='tight')
print("✓ Map saved as 'grid_station_map.png'")

# Print distance summary
print("\nDistance Summary:")
print("-" * 50)
for station in stations:
    lat = station["lat"]
    lon = station["lon"]
    name = station["name"]
    _, _, distance = find_nearest_grid_point(lat, lon, grid_lats, grid_lons)
    print(f"{name:20s} {distance:6.2f} km")