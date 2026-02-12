#!/usr/bin/env python3
"""
Interactive map using Plotly + Mapbox (reads API key from environment)
ECMWF 0.25° grid vs Irish stations - FULLY DEBUGGED VERSION
Fixes: NaN errors, WebGL issues, and all previous bugs
"""

import json
import numpy as np
import os
from pathlib import Path

print("=" * 60)
print("DEBUG: Script starting...")
print("=" * 60)

# Check plotly
try:
    import plotly.graph_objects as go
    print("✓ DEBUG: Plotly imported successfully")
except ImportError:
    print("ERROR: plotly is not installed!")
    print("Install it with: pip install plotly")
    exit(1)

# Get Mapbox token from environment
print("\nDEBUG: Looking for Mapbox API key in environment...")
MAPBOX_TOKEN = os.environ.get('MAPBOX_TOKEN') or os.environ.get('MAPBOX_API_KEY')

if not MAPBOX_TOKEN:
    print("ERROR: Mapbox API key not found!")
    print("Available env vars:", list(os.environ.keys())[:10], "...")
    print("Set it with: export MAPBOX_TOKEN='your_key_here'")
    print("Or: export MAPBOX_API_KEY='your_key_here'")
    exit(1)

print(f"✓ DEBUG: Found Mapbox API key: {MAPBOX_TOKEN[:10]}... (length: {len(MAPBOX_TOKEN)})")

# Load station data - TRY MULTIPLE PATHS
print("\nDEBUG: Looking for stations.json...")
possible_paths = [
    Path("stations.json"),
    Path("../stations.json"),
    Path("../../stations.json"),
    Path(__file__).parent / "stations.json",
    Path(__file__).parent.parent / "stations.json",
    Path("/mnt/user-data/uploads/stations.json"),
]

for i, path in enumerate(possible_paths):
    print(f"  Checking path {i+1}: {path.absolute()} ... {'EXISTS' if path.exists() else 'not found'}")

data = None
for path in possible_paths:
    if path.exists():
        print(f"✓ DEBUG: Found stations file at: {path}")
        try:
            with open(path, "r") as f:
                data = json.load(f)
            print(f"  DEBUG: Loaded JSON successfully")
            
            # Validate structure
            if "stations" not in data:
                print("ERROR: JSON missing 'stations' key!")
                data = None
                continue
                
            print(f"  DEBUG: Found {len(data.get('stations', {}))} station categories")
            break
        except json.JSONDecodeError as e:
            print(f"ERROR: Invalid JSON in {path}: {e}")
            continue
        except Exception as e:
            print(f"ERROR: Failed to read {path}: {e}")
            continue

if data is None:
    print("ERROR: Could not find or load valid stations.json file!")
    exit(1)

# Extract all stations
print("\nDEBUG: Extracting stations from JSON...")
stations = []
for category in ["onshore", "coastal", "offshore"]:
    category_stations = data["stations"].get(category, [])
    count = len(category_stations)
    print(f"  DEBUG: Found {count} {category} stations")
    for station in category_stations:
        # Validate station has required fields
        if not all(key in station for key in ["name", "latitude", "longitude"]):
            print(f"  WARNING: Skipping invalid station: {station}")
            continue
            
        stations.append({
            "name": station["name"],
            "lat": station["latitude"],
            "lon": station["longitude"],
            "type": category
        })

if not stations:
    print("ERROR: No valid stations found!")
    exit(1)

print(f"✓ DEBUG: Total stations loaded: {len(stations)}")
for s in stations:
    print(f"    - {s['name']}: ({s['lat']:.3f}, {s['lon']:.3f}) [{s['type']}]")

# Define Irish domain
LAT_MIN, LAT_MAX = 50.0, 56.0
LON_MIN, LON_MAX = -16.5, -5.0

print(f"\nDEBUG: Generating grid...")
print(f"  Domain: {LAT_MIN}°N to {LAT_MAX}°N, {LON_MIN}°E to {LON_MAX}°E")

# Generate 0.25° grid
RESOLUTION = 0.25
lats = np.arange(LAT_MIN, LAT_MAX + RESOLUTION, RESOLUTION)
lons = np.arange(LON_MIN, LON_MAX + RESOLUTION, RESOLUTION)
grid_lons, grid_lats = np.meshgrid(lons, lats)

print(f"✓ DEBUG: Grid generated: {len(lats)} x {len(lons)} = {grid_lats.size} points")
print(f"  Resolution: {RESOLUTION}°")

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate distance in km using Haversine formula"""
    R = 6371  # Earth radius in km
    lat1, lon1, lat2, lon2 = map(np.radians, [lat1, lon1, lat2, lon2])
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    a = np.sin(dlat/2)**2 + np.cos(lat1) * np.cos(lat2) * np.sin(dlon/2)**2
    c = 2 * np.arcsin(np.sqrt(np.clip(a, 0, 1)))  # Clip to avoid numerical errors
    return R * c

def find_nearest_grid_point(lat, lon, grid_lats, grid_lons):
    """Find nearest grid point and return coordinates and distance"""
    distances = haversine_distance(lat, lon, grid_lats, grid_lons)
    idx = np.unravel_index(np.argmin(distances), distances.shape)
    nearest_lat = grid_lats[idx]
    nearest_lon = grid_lons[idx]
    distance = distances[idx]
    return nearest_lat, nearest_lon, distance

def format_lon(lon):
    """Format longitude with proper E/W designation"""
    if lon < 0:
        return f"{abs(lon):.3f}°W"
    else:
        return f"{lon:.3f}°E"

def format_lat(lat):
    """Format latitude with proper N/S designation"""
    if lat >= 0:
        return f"{lat:.3f}°N"
    else:
        return f"{abs(lat):.3f}°S"

# Create figure with mapbox
print("\nDEBUG: Creating Plotly figure...")
fig = go.Figure()

# Add grid points (sample every 4th to reduce clutter)
sample_rate = 4
grid_sample = grid_lons.flatten()[::sample_rate]
grid_sample_size = len(grid_sample)
print(f"DEBUG: Adding {grid_sample_size} grid points (sampled every {sample_rate}th)")
fig.add_trace(go.Scattermapbox(
    lon=grid_lons.flatten()[::sample_rate],
    lat=grid_lats.flatten()[::sample_rate],
    mode='markers',
    marker=dict(size=3, color='lightcoral', opacity=0.3),
    name='ECMWF 0.25° grid',
    hoverinfo='skip',
    showlegend=True
))

# Color map for station types
colors = {"onshore": "green", "coastal": "orange", "offshore": "blue"}

print(f"DEBUG: Adding stations and connections...")

# Group stations by type for cleaner legend
station_traces = {"onshore": [], "coastal": [], "offshore": []}
grid_highlight_lons = []
grid_highlight_lats = []

# FIXED: Create separate traces for each connection line instead of using None
connection_traces = []

for station in stations:
    lat = station["lat"]
    lon = station["lon"]
    name = station["name"]
    stype = station["type"]
    
    # Find nearest grid point
    nearest_lat, nearest_lon, distance = find_nearest_grid_point(
        lat, lon, grid_lats, grid_lons
    )
    
    print(f"  Station {name}: distance to grid = {distance:.2f} km")
    
    # FIXED: Store each connection as a separate trace to avoid NaN issues
    connection_traces.append({
        'lons': [lon, nearest_lon],
        'lats': [lat, nearest_lat],
        'name': name
    })
    
    # Collect grid highlight points
    grid_highlight_lons.append(nearest_lon)
    grid_highlight_lats.append(nearest_lat)
    
    # Collect station data by type
    station_traces[stype].append({
        'lon': lon,
        'lat': lat,
        'name': name,
        'distance': distance,
        'nearest_lon': nearest_lon,
        'nearest_lat': nearest_lat
    })

# FIXED: Add connection lines individually but with showlegend=False after first
print(f"DEBUG: Adding {len(connection_traces)} connection lines")
for i, conn in enumerate(connection_traces):
    fig.add_trace(go.Scattermapbox(
        lon=conn['lons'],
        lat=conn['lats'],
        mode='lines',
        line=dict(width=2, color='red'),
        name='Station↔Grid connections' if i == 0 else '',
        hoverinfo='skip',
        showlegend=(i == 0),  # Only show legend for first connection
        legendgroup='connections'  # Group them together
    ))

# Add all grid highlights as a single trace
print(f"DEBUG: Adding grid highlights")
fig.add_trace(go.Scattermapbox(
    lon=grid_highlight_lons,
    lat=grid_highlight_lats,
    mode='markers',
    marker=dict(size=10, color='darkred', symbol='square', opacity=0.7),
    name='Nearest grid points',
    hoverinfo='skip',
    showlegend=True
))

# Add stations grouped by type
for stype, color in colors.items():
    if stype not in station_traces or not station_traces[stype]:
        continue
    
    trace_data = station_traces[stype]
    lons = [s['lon'] for s in trace_data]
    lats = [s['lat'] for s in trace_data]
    names = [s['name'] for s in trace_data]
    
    hover_texts = [
        f"<b>{s['name']}</b><br>" +
        f"Type: {stype}<br>" +
        f"Location: {format_lat(s['lat'])}, {format_lon(s['lon'])}<br>" +
        f"Distance to grid: {s['distance']:.2f} km"
        for s in trace_data
    ]
    
    print(f"DEBUG: Adding {len(trace_data)} {stype} stations")
    fig.add_trace(go.Scattermapbox(
        lon=lons,
        lat=lats,
        mode='markers+text',
        marker=dict(size=12, color=color),
        text=names,
        textposition='top center',
        textfont=dict(size=10, color='black', family='Arial Black'),
        name=f'{stype.capitalize()} stations',
        hovertext=hover_texts,
        hoverinfo='text',
        showlegend=True
    ))

print(f"✓ DEBUG: All traces added to figure")

# Update layout with Mapbox
print("\nDEBUG: Configuring map layout...")
print(f"  Map style: outdoors")
print(f"  Center: 53°N, 8°W")
print(f"  Initial zoom: 5.5")

fig.update_layout(
    mapbox=dict(
        accesstoken=MAPBOX_TOKEN,
        style='outdoors',
        center=dict(lat=53, lon=-8),
        zoom=5.5
    ),
    title=dict(
        text='ECMWF 0.25° Grid vs Irish Station Locations<br>'
             '<sub>Interactive: Zoom/pan with mouse • Hover for details • Click legend to toggle layers</sub>',
        x=0.5,
        xanchor='center',
        font=dict(size=16)
    ),
    height=900,
    showlegend=True,
    legend=dict(
        x=0.02,
        y=0.98,
        bgcolor='rgba(255,255,255,0.95)',
        bordercolor='black',
        borderwidth=1,
        font=dict(size=11)
    ),
    margin=dict(l=0, r=0, t=80, b=0),
    hovermode='closest'
)

print("✓ DEBUG: Layout configured")

# Save HTML
output_file = 'grid_station_map_mapbox_FINAL.html'
print(f"\nDEBUG: Writing HTML to {output_file}...")

try:
    fig.write_html(output_file, include_plotlyjs='cdn')
    print(f"✓ DEBUG: HTML file written successfully")
    
    # Add comprehensive JavaScript debugging and error handling
    print("DEBUG: Injecting JavaScript console logs and error handling...")
    with open(output_file, 'r') as f:
        html_content = f.read()
    
    # Inject enhanced debug script with WebGL fallback info
    debug_script = f"""
    <script>
    console.log("=== MAPBOX MAP DEBUG ===");
    console.log("Map initialized");
    console.log("Mapbox token length:", {len(MAPBOX_TOKEN)});
    console.log("Stations loaded:", {len(stations)});
    console.log("Grid points:", {grid_lats.size});
    console.log("Grid sample shown:", {grid_sample_size});
    console.log("Connection traces:", {len(connection_traces)});
    
    // Check WebGL support
    function checkWebGL() {{
        try {{
            const canvas = document.createElement('canvas');
            const gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');
            if (gl && gl instanceof WebGLRenderingContext) {{
                console.log("✓ WebGL is supported");
                console.log("  Renderer:", gl.getParameter(gl.RENDERER));
                console.log("  Vendor:", gl.getParameter(gl.VENDOR));
                return true;
            }} else {{
                console.error("✗ WebGL is NOT supported!");
                return false;
            }}
        }} catch (e) {{
            console.error("✗ Error checking WebGL:", e);
            return false;
        }}
    }}
    
    if (!checkWebGL()) {{
        console.error("SOLUTION: Enable hardware acceleration in your browser:");
        console.error("  Chrome: chrome://settings → System → Use hardware acceleration");
        console.error("  Firefox: about:config → webgl.force-enabled → true");
        console.error("  Or try a different browser");
    }}
    
    // Error monitoring
    window.addEventListener('error', function(e) {{
        console.error("ERROR:", e.message);
        console.error("  at:", e.filename, "line", e.lineno);
        
        if (e.message.includes('WebGL')) {{
            console.error("WebGL ERROR DETECTED!");
            console.error("This is likely due to:");
            console.error("  1. Hardware acceleration disabled");
            console.error("  2. Outdated graphics drivers");
            console.error("  3. Browser WebGL blacklist");
            console.error("  4. Running in virtual machine/remote desktop");
        }}
    }});
    
    // Check Plotly
    if (typeof Plotly !== 'undefined') {{
        console.log("✓ Plotly loaded successfully");
        console.log("  Version:", Plotly.version);
    }} else {{
        console.error("✗ Plotly failed to load!");
    }}
    
    // Check for map rendering
    setTimeout(function() {{
        const mapContainer = document.querySelector('.mapboxgl-map, .maplibregl-map');
        if (mapContainer) {{
            console.log("✓ Map container found");
        }} else {{
            console.error("✗ Map container not found!");
            console.error("Troubleshooting:");
            console.error("  1. Check WebGL support (see above)");
            console.error("  2. Check network tab for failed requests");
            console.error("  3. Verify Mapbox token is valid");
            console.error("  4. Try a different browser");
            
            // Show user-friendly error
            const errorDiv = document.createElement('div');
            errorDiv.style.cssText = 'position:fixed;top:50%;left:50%;transform:translate(-50%,-50%);background:white;padding:20px;border:2px solid red;border-radius:8px;max-width:500px;z-index:9999;';
            errorDiv.innerHTML = `
                <h2 style="color:red;margin-top:0;">Map Failed to Load</h2>
                <p><strong>Possible causes:</strong></p>
                <ul>
                    <li>WebGL is disabled or not supported</li>
                    <li>Hardware acceleration is off</li>
                    <li>Graphics drivers need updating</li>
                    <li>Running in VM or remote desktop</li>
                </ul>
                <p><strong>Solutions:</strong></p>
                <ol>
                    <li>Enable hardware acceleration in browser settings</li>
                    <li>Update graphics drivers</li>
                    <li>Try Chrome or Firefox</li>
                    <li>Check browser console (F12) for details</li>
                </ol>
                <button onclick="this.parentElement.remove()">Close</button>
            `;
            document.body.appendChild(errorDiv);
        }}
    }}, 3000);
    </script>
    """
    
    html_content = html_content.replace('</body>', debug_script + '</body>')
    
    with open(output_file, 'w') as f:
        f.write(html_content)
    
    print("✓ DEBUG: JavaScript console logs and error handling injected")
    
except Exception as e:
    print(f"✗ ERROR writing HTML: {e}")
    import traceback
    traceback.print_exc()
    exit(1)

print(f"\n{'='*60}")
print(f"✓ SUCCESS: Interactive map saved as '{output_file}'")
print(f"  Full path: {Path(output_file).absolute()}")
print(f"  Open in browser and press F12 to see console debug logs")
print(f"\n  If map doesn't load, check console for WebGL errors")
print(f"  Solution: Enable hardware acceleration in browser settings")
print(f"{'='*60}")

# Print distance summary
print("\n" + "="*60)
print("DISTANCE SUMMARY:")
print("="*60)
station_distances = []
for station in stations:
    lat = station["lat"]
    lon = station["lon"]
    name = station["name"]
    _, _, distance = find_nearest_grid_point(lat, lon, grid_lats, grid_lons)
    station_distances.append((name, distance))
    print(f"{name:25s} {distance:6.2f} km")

# Statistics
distances_only = [d for _, d in station_distances]
print("="*60)
print(f"Average distance: {np.mean(distances_only):.2f} km")
print(f"Max distance:     {np.max(distances_only):.2f} km ({station_distances[np.argmax(distances_only)][0]})")
print(f"Min distance:     {np.min(distances_only):.2f} km ({station_distances[np.argmin(distances_only)][0]})")
print("="*60)