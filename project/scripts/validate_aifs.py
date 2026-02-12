#!/usr/bin/env python3
"""
Validate AIFS forecasts against Shannon Airport observations
Shows forecast skill degradation over lead time
"""

import xarray as xr
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Configuration
DATA_DIR = Path("/home/chantelle/Desktop/PhD Project/code/aifs_wind/project/data/ecmwf_forecasts")
OBS_FILE = Path("/home/chantelle/Desktop/PhD Project/code/aifs_wind/project/data/met/hly518.csv")
OUTPUT_DIR = Path("/home/chantelle/Desktop/PhD Project/code/aifs_wind/project/plots")
OUTPUT_DIR.mkdir(exist_ok=True)

# Shannon Airport location
STATION_LAT = 52.69
STATION_LON = -8.918
STATION_NAME = "Shannon Airport"

# Analysis setup
INIT_DATE = "20260209"  # Feb 9, 2026
INIT_TIME = "00z"
LEAD_TIMES = [0, 6, 12, 24, 48, 72, 96, 120, 144]

print("="*80)
print(f"AIFS Forecast Validation vs {STATION_NAME}")
print(f"Init: {INIT_DATE} {INIT_TIME}")
print("="*80)

def read_grib_wind(filepath, lat, lon):
    """Extract 10u and 10v wind components at nearest grid point"""
    try:
        ds = xr.open_dataset(filepath, engine='cfgrib', 
                             backend_kwargs={'filter_by_keys': {'typeOfLevel': 'heightAboveGround', 'level': 10}})
        ds_point = ds.sel(latitude=lat, longitude=lon, method='nearest')
        
        u = ds_point['u10'].values if 'u10' in ds_point else None
        v = ds_point['v10'].values if 'v10' in ds_point else None
        
        if u is not None and v is not None:
            speed = np.sqrt(u**2 + v**2)
            return float(speed)
        return None
    except Exception as e:
        return None

# ============================================================================
# 1. READ AIFS-SINGLE FORECASTS
# ============================================================================
print("\n1. Reading AIFS-Single forecasts...")
forecast_data = []

for step in LEAD_TIMES:
    filepath = DATA_DIR / "aifs-single" / "oper" / f"date{INIT_DATE}" / INIT_TIME / "type-fc" / "levtype-sfc" / f"step-{step:03d}h.grib2"
    
    if filepath.exists():
        wind = read_grib_wind(filepath, STATION_LAT, STATION_LON)
        if wind is not None:
            # Calculate valid time
            init_dt = datetime.strptime(INIT_DATE + INIT_TIME[:2], "%Y%m%d%H")
            valid_dt = init_dt + timedelta(hours=step)
            forecast_data.append({
                'lead_time': step,
                'valid_time': valid_dt,
                'forecast_wind': wind
            })
            print(f"  Step {step:03d}h: {wind:.2f} m/s (valid: {valid_dt})")

forecast_df = pd.DataFrame(forecast_data)
print(f"\nAIFS-Single: {len(forecast_df)} forecast points")

# ============================================================================
# 2. READ SHANNON OBSERVATIONS
# ============================================================================
print("\n2. Reading Shannon observations...")

# Read CSV - skip first 23 rows, row 24 becomes header
obs_df = pd.read_csv(OBS_FILE, skiprows=23, on_bad_lines='skip')

# Parse date column (format: DD-MMM-YYYY HH:MM)
obs_df['datetime'] = pd.to_datetime(obs_df['date'], format='%d-%b-%Y %H:%M')

# Convert wind speed from knots to m/s (handle non-numeric values)
KNOTS_TO_MS = 0.514444
obs_df['wdsp_numeric'] = pd.to_numeric(obs_df['wdsp'], errors='coerce')
obs_df['wind_ms'] = obs_df['wdsp_numeric'] * KNOTS_TO_MS

# Filter to Feb 9-15, 2026 and remove rows with missing wind data
start_date = datetime(2026, 2, 9, 0, 0)
end_date = datetime(2026, 2, 15, 23, 59)
obs_filtered = obs_df[(obs_df['datetime'] >= start_date) & 
                      (obs_df['datetime'] <= end_date) & 
                      (obs_df['wind_ms'].notna())].copy()

print(f"Shannon observations: {len(obs_filtered)} hourly points")
if len(obs_filtered) > 0:
    print(f"  Date range: {obs_filtered['datetime'].min()} to {obs_filtered['datetime'].max()}")
    print(f"  Wind range: {obs_filtered['wind_ms'].min():.2f} - {obs_filtered['wind_ms'].max():.2f} m/s")
else:
    print("  WARNING: No observations found for Feb 9-15, 2026!")
    print("  The file may not contain data for these dates yet.")

# ============================================================================
# 3. MATCH FORECASTS TO OBSERVATIONS
# ============================================================================
print("\n3. Matching forecasts to observations...")

matched_data = []
for idx, row in forecast_df.iterrows():
    valid_time = row['valid_time']
    forecast_wind = row['forecast_wind']
    lead_time = row['lead_time']
    
    # Find matching observation (within 30 minutes)
    time_diff = abs(obs_filtered['datetime'] - valid_time)
    if time_diff.min() < timedelta(minutes=30):
        match_idx = time_diff.idxmin()
        obs_wind = obs_filtered.loc[match_idx, 'wind_ms']
        
        matched_data.append({
            'lead_time': lead_time,
            'valid_time': valid_time,
            'forecast': forecast_wind,
            'observed': obs_wind,
            'error': forecast_wind - obs_wind,
            'abs_error': abs(forecast_wind - obs_wind)
        })
        print(f"  {valid_time}: Forecast={forecast_wind:.2f} m/s, Observed={obs_wind:.2f} m/s, Error={forecast_wind-obs_wind:+.2f} m/s")

matched_df = pd.DataFrame(matched_data)
print(f"\nMatched pairs: {len(matched_df)}")

# ============================================================================
# 4. CREATE VALIDATION PLOTS
# ============================================================================

if len(matched_df) == 0:
    print("\nERROR: No matched forecast-observation pairs!")
    print("Cannot create validation plot. Check that observation data covers the forecast period.")
    exit(1)

fig, axes = plt.subplots(2, 1, figsize=(14, 10))
fig.suptitle(f'AIFS-Single Forecast Validation vs {STATION_NAME}\n'
             f'Init: {INIT_DATE} {INIT_TIME}', 
             fontsize=16, fontweight='bold')

# -------------------------
# PLOT 1: Forecast vs Observed
# -------------------------
ax = axes[0]
ax.plot(matched_df['valid_time'], matched_df['forecast'], 'b-o', 
        linewidth=2, markersize=8, label='AIFS-Single Forecast')
ax.plot(matched_df['valid_time'], matched_df['observed'], 'r-s', 
        linewidth=2, markersize=8, label='Shannon Observed')

ax.set_ylabel('10m Wind Speed (m/s)', fontsize=12)
ax.set_title('Forecast vs Observed Wind Speed', fontsize=13, fontweight='bold')
ax.grid(True, alpha=0.3)
ax.legend(fontsize=11)
ax.tick_params(axis='x', rotation=45)

# -------------------------
# PLOT 2: Forecast Error vs Lead Time
# -------------------------
ax = axes[1]
ax.plot(matched_df['lead_time'], matched_df['error'], 'go-', 
        linewidth=2, markersize=8, label='Forecast Error')
ax.axhline(y=0, color='k', linestyle='--', alpha=0.5)
ax.fill_between(matched_df['lead_time'], 0, matched_df['error'], 
                alpha=0.3, color='green')

ax.set_xlabel('Forecast Lead Time (hours)', fontsize=12)
ax.set_ylabel('Error (Forecast - Observed) [m/s]', fontsize=12)
ax.set_title('Forecast Error vs Lead Time (Skill Degradation)', fontsize=13, fontweight='bold')
ax.grid(True, alpha=0.3)
ax.legend(fontsize=11)

plt.tight_layout()

# Save
output_file = OUTPUT_DIR / f"aifs_validation_{INIT_DATE}_{INIT_TIME}_Shannon.png"
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"\n✓ Validation plot saved: {output_file}")

plt.show()

# ============================================================================
# 5. SUMMARY STATISTICS
# ============================================================================
print("\n" + "="*80)
print("VALIDATION SUMMARY")
print("="*80)
print(f"Matched pairs:     {len(matched_df)}")
print(f"\nForecast statistics:")
print(f"  Mean wind:       {matched_df['forecast'].mean():.2f} m/s")
print(f"  Std dev:         {matched_df['forecast'].std():.2f} m/s")
print(f"\nObserved statistics:")
print(f"  Mean wind:       {matched_df['observed'].mean():.2f} m/s")
print(f"  Std dev:         {matched_df['observed'].std():.2f} m/s")
print(f"\nError statistics:")
print(f"  Mean error (bias): {matched_df['error'].mean():+.2f} m/s")
print(f"  Mean absolute error: {matched_df['abs_error'].mean():.2f} m/s")
print(f"  RMSE:            {np.sqrt((matched_df['error']**2).mean()):.2f} m/s")
print(f"\nError by lead time:")
for lead in sorted(matched_df['lead_time'].unique()):
    subset = matched_df[matched_df['lead_time'] == lead]
    mae = subset['abs_error'].mean()
    print(f"  {lead:3d}h: MAE = {mae:.2f} m/s")

print("="*80)
print("✓ Validation complete!")
