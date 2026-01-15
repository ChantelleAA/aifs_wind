#!/usr/bin/env python3
"""
Generate a map of Irish weather station and buoy locations using Cartopy
"""

import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature
from matplotlib.patches import Rectangle
import numpy as np

# Station coordinates
locations = {
    # ONSHORE (Met Éireann Synop Stations)
    'Shannon Airport': {'lat': 52.702, 'lon': -8.925, 'type': 'onshore'},
    'Cork Airport': {'lat': 51.841, 'lon': -8.491, 'type': 'onshore'},
    
    # COASTAL (Met Éireann Synop Stations)
    'Malin Head': {'lat': 55.367, 'lon': -7.333, 'type': 'coastal'},
    'Valentia': {'lat': 51.939, 'lon': -10.243, 'type': 'coastal'},
    'Mace Head': {'lat': 53.326, 'lon': -9.904, 'type': 'coastal'},
    'Sherkin Island': {'lat': 51.469, 'lon': -9.428, 'type': 'coastal'},
    
    # OFFSHORE (Marine Institute Buoys)
    'M2 Buoy': {'lat': 53.485, 'lon': -5.425, 'type': 'offshore', 'sea': 'Irish Sea'},
    'M3 Buoy': {'lat': 51.217, 'lon': -6.703, 'type': 'offshore', 'sea': 'Celtic Sea'},
    'M4 Buoy': {'lat': 53.062, 'lon': -11.208, 'type': 'offshore', 'sea': 'Atlantic'},
    'M5 Buoy': {'lat': 51.690, 'lon': -11.760, 'type': 'offshore', 'sea': 'Atlantic'},
    'M6 Buoy': {'lat': 51.219, 'lon': -10.555, 'type': 'offshore', 'sea': 'Atlantic'},
}

# Create figure with Cartopy projection
fig = plt.figure(figsize=(14, 12))
ax = plt.axes(projection=ccrs.PlateCarree())

# Set map extent to focus on Ireland and surrounding waters
# Format: [lon_min, lon_max, lat_min, lat_max]
ax.set_extent([-12.5, -4.5, 50.5, 56], crs=ccrs.PlateCarree())

# Add map features
ax.add_feature(cfeature.LAND, facecolor='#E8E8E8', edgecolor='none', zorder=1)
ax.add_feature(cfeature.OCEAN, facecolor='#C6ECFF', zorder=0)
ax.add_feature(cfeature.COASTLINE, linewidth=0.8, edgecolor='#333333', zorder=2)
ax.add_feature(cfeature.BORDERS, linewidth=0.5, edgecolor='#666666', linestyle='--', zorder=2)

# Add gridlines
gl = ax.gridlines(draw_labels=True, linewidth=0.5, color='gray', alpha=0.5, linestyle='--')
gl.top_labels = False
gl.right_labels = False
gl.xlabel_style = {'size': 11}
gl.ylabel_style = {'size': 11}

# Define colors and markers for different location types
style_config = {
    'onshore': {
        'color': '#27AE60',  # Green
        'marker': 's',        # Square
        'size': 200,
        'label': 'Onshore (Met Éireann)',
        'edgecolor': 'white',
        'linewidth': 2
    },
    'coastal': {
        'color': '#F39C12',  # Orange
        'marker': '^',        # Triangle
        'size': 200,
        'label': 'Coastal (Met Éireann)',
        'edgecolor': 'white',
        'linewidth': 2
    },
    'offshore': {
        'color': '#16A085',  # Teal
        'marker': 'o',        # Circle
        'size': 200,
        'label': 'Offshore (Marine Institute)',
        'edgecolor': 'white',
        'linewidth': 2
    }
}

# Plot locations by type
plotted_types = set()
for name, info in locations.items():
    loc_type = info['type']
    style = style_config[loc_type]
    
    # Plot marker
    ax.scatter(
        info['lon'], info['lat'],
        marker=style['marker'],
        s=style['size'],
        c=style['color'],
        edgecolors=style['edgecolor'],
        linewidths=style['linewidth'],
        transform=ccrs.PlateCarree(),
        zorder=10,
        label=style['label'] if loc_type not in plotted_types else ""
    )
    plotted_types.add(loc_type)
    
    # Add text annotation with white background box
    # Adjust text position based on location to avoid overlap
    text_offset_x = 0.09
    text_offset_y = 0.09
    
    # Special positioning for specific stations to avoid overlap
    if name == 'Sherkin Island':
        text_offset_x = -0.09
        text_offset_y = -0.09
    elif name == 'Cork Airport':
        text_offset_x = 0.09
        text_offset_y = 0.09
    elif name == 'Shannon Airport':
        text_offset_x = 0.09
        text_offset_y = -0.09
    elif name == 'Valentia':
        text_offset_x = -0.09
        text_offset_y = 0.09
    elif name == 'M5 Buoy':
        text_offset_x = 0.09
        text_offset_y = -0.09
    elif name == 'M6 Buoy':
        text_offset_x = 0.09
        text_offset_y = -0.09
    elif name == 'M3 Buoy':
        text_offset_x = -0.09
        text_offset_y = 0.09
    elif name == 'Mace Head':
        text_offset_x = -0.09
        text_offset_y = 0.0
    elif name == 'M4 Buoy':
        text_offset_x = -0.09
        text_offset_y = 0.09
    elif name == 'Malin Head':
        text_offset_x = 0.09
        text_offset_y = 0.09
    elif name == 'M2 Buoy':
        text_offset_x = 0.09
        text_offset_y = -0.09
    
    # Add label with sea name for buoys
    if 'sea' in info:
        label_text = f"{name}\n({info['sea']})"
    else:
        label_text = name
    
    ax.text(
        info['lon'] + text_offset_x, info['lat'] + text_offset_y,
        label_text,
        transform=ccrs.PlateCarree(),
        fontsize=9,
        fontweight='bold',
        ha='left' if text_offset_x > 0 else 'right',
        va='bottom' if text_offset_y > 0 else 'top',
        bbox=dict(
            boxstyle='round,pad=0.4',
            facecolor='white',
            edgecolor=style['color'],
            linewidth=1.5,
            alpha=0.9
        ),
        zorder=11
    )

# Add title
ax.set_title(
    'Irish Weather Station and Buoy Locations\nAIFS Wind Forecast Evaluation Study',
    fontsize=18,
    fontweight='bold',
    pad=20
)

# Add legend
legend = ax.legend(
    loc='lower left',
    fontsize=11,
    frameon=True,
    fancybox=True,
    shadow=True,
    title='Location Types',
    title_fontsize=12
)
legend.get_frame().set_facecolor('white')
legend.get_frame().set_alpha(0.95)

# Add statistics box
stats_text = (
    f"Total Locations: 11\n"
    f"• Onshore: 2\n"
    f"• Coastal: 4\n"
    f"• Offshore: 5"
)
ax.text(
    0.02, 0.98,
    stats_text,
    transform=ax.transAxes,
    fontsize=11,
    verticalalignment='top',
    bbox=dict(
        boxstyle='round,pad=0.7',
        facecolor='lightyellow',
        edgecolor='#2C3E50',
        linewidth=2,
        alpha=0.95
    ),
    zorder=15
)

# Adjust layout
plt.tight_layout()

# Save figure
output_path = 'irish_stations_map.png'
plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
print(f"\n✓ Map saved to: {output_path}")

# Also save a high-resolution version
output_path_hires = 'irish_stations_map_hires.png'
plt.savefig(output_path_hires, dpi=600, bbox_inches='tight', facecolor='white')
print(f"✓ High-res map saved to: {output_path_hires}")

plt.show()

print("\n" + "="*80)
print("MAP GENERATION COMPLETE")
print("="*80)
print("\nStation Summary:")
print(f"{'Location':<20} {'Type':<12} {'Latitude':<10} {'Longitude':<10} {'Sea':<15}")
print("-" * 80)
for name, info in sorted(locations.items()):
    sea = info.get('sea', 'N/A')
    print(f"{name:<20} {info['type']:<12} {info['lat']:<10.3f} {info['lon']:<10.3f} {sea:<15}")