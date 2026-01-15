#!/usr/bin/env python3
"""
Data Inspection Script - Updated for ecmwf_forecasts structure

This script examines all available forecast data downloaded with the new structure:
  ecmwf_forecasts/
    ├── ifs/oper/date-N/HHz/type-fc/step-NNNh.grib2
    ├── aifs-single/oper/date-N/HHz/type-fc/step-NNNh.grib2
    └── aifs-ens/enfo/date-N/HHz/type-cf|pf/step-NNNh.grib2

Usage:
    python inspect_data_updated.py
"""

import pandas as pd
import numpy as np
import xarray as xr
from pathlib import Path
import sys
from datetime import datetime

print("=" * 80)
print("WIND FORECAST DATA INSPECTION (Updated Structure)")
print("=" * 80)

# ============================================================================
# 1. CHECK FORECAST DATA (NEW STRUCTURE)
# ============================================================================

print("\n" + "=" * 80)
print("1. ECMWF FORECAST DATA")
print("=" * 80)

FORECAST_BASE = Path("ecmwf_forecasts")

models = {
    'IFS': FORECAST_BASE / "ifs" / "oper",
    'AIFS Single': FORECAST_BASE / "aifs-single" / "oper",
    'AIFS Ensemble': FORECAST_BASE / "aifs-ens" / "enfo"
}

if not FORECAST_BASE.exists():
    print(f"\n✗ Forecast directory not found: {FORECAST_BASE.absolute()}")
    print("  Run the download script first!")
else:
    for model_name, model_path in models.items():
        print(f"\n{model_name}:")
        print(f"  Path: {model_path}")
        
        if not model_path.exists():
            print(f"  ✗ Directory not found")
            continue
        
        # Count files
        all_grib_files = list(model_path.rglob("*.grib2"))
        
        if not all_grib_files:
            print(f"  ✗ No GRIB files found")
            continue
        
        print(f"  ✓ Found {len(all_grib_files)} GRIB2 files")
        
        # Analyze structure
        dates = set()
        times = set()
        types = set()
        steps = set()
        
        for f in all_grib_files:
            # Parse path: date-N/HHz/type-XX/step-NNNh.grib2
            parts = f.parts
            for part in parts:
                if part.startswith('date'):
                    dates.add(part)
                if part.endswith('z'):
                    times.add(part)
                if part.startswith('type-'):
                    types.add(part)
                if part.startswith('step-'):
                    step_str = part.replace('step-', '').replace('h.grib2', '')
                    try:
                        steps.add(int(step_str))
                    except:
                        pass
        
        print(f"  Dates: {sorted(dates)}")
        print(f"  Init times: {sorted(times)}")
        print(f"  Types: {sorted(types)}")
        print(f"  Lead times: {sorted(steps)} hours")
        
        # Try to open one file
        if all_grib_files:
            test_file = all_grib_files[0]
            print(f"\n  Testing file: {test_file.name}")
            try:
                ds = xr.open_dataset(test_file, engine='cfgrib')
                print(f"    ✓ File readable")
                print(f"    Variables: {', '.join(list(ds.data_vars)[:10])}")
                
                # Check for wind variables
                wind_vars = [v for v in ds.data_vars if any(x in str(v).lower() for x in ['u10', 'v10', 'wind', '10u', '10v'])]
                if wind_vars:
                    print(f"    Wind variables: {', '.join(wind_vars)}")
                    
                    # Check dimensions
                    for var in wind_vars[:1]:  # Check first wind variable
                        print(f"    {var} shape: {ds[var].shape}")
                        print(f"    Coordinates: {list(ds[var].coords)}")
                
                ds.close()
            except Exception as e:
                print(f"    ✗ Error reading file: {e}")
        
        # Calculate total size
        total_size = sum(f.stat().st_size for f in all_grib_files) / (1024**3)  # GB
        print(f"\n  Total data size: {total_size:.2f} GB")

# ============================================================================
# 2. INSPECT MET ÉIREANN STATION DATA
# ============================================================================

print("\n" + "=" * 80)
print("2. MET ÉIREANN STATION DATA")
print("=" * 80)

station_files = {
    'Phoenix Park': 'data/Met eireann/hourly-dublin-pheonixpark/hly175.csv',
    'Shannon Airport': 'data/Met eireann/hourly-clare-shannonairport/hly518.csv',
    'Cork Airport': 'data/Met eireann/hourly-cork-corkairport/hly3904.csv',
    'Malin Head': 'data/Met eireann/hourly-donegal-malinhead/hly1575.csv',
    'Valentia': 'data/Met eireann/hourly-kerry-valentia/hly2275.csv',
    'Mace Head': 'data/Met eireann/houryl-galway-macehead/hly275.csv',
    'Sherkin Island': 'data/Met eireann/hourly-cork-sherkin/hly775.csv'
}

for station_name, filepath in station_files.items():
    print(f"\n{station_name}:")
    print(f"  File: {filepath}")
    
    try:
        df = pd.read_csv(filepath, nrows=5)
        print(f"  ✓ File exists and readable")
        print(f"  Columns: {', '.join(df.columns.tolist()[:10])}")
        
        # Try to load full file
        try:
            df_full = pd.read_csv(filepath)
            print(f"  Total rows: {len(df_full)}")
            
            # Find date column
            date_cols = [col for col in df_full.columns if 'date' in col.lower()]
            if date_cols:
                dates = pd.to_datetime(df_full[date_cols[0]], errors='coerce')
                print(f"  Date range: {dates.min()} to {dates.max()}")
            
            # Find wind columns
            wind_cols = [col for col in df_full.columns 
                        if any(x in col.lower() for x in ['wind', 'wdsp', 'ws'])]
            if wind_cols:
                print(f"  Wind columns: {', '.join(wind_cols)}")
                
        except Exception as e:
            print(f"  Warning loading full file: {e}")
            
    except FileNotFoundError:
        print(f"  ✗ File not found")
    except Exception as e:
        print(f"  ✗ Error reading file: {e}")

# ============================================================================
# 3. INSPECT ERA5 DATA
# ============================================================================

print("\n" + "=" * 80)
print("3. ERA5 REANALYSIS DATA")
print("=" * 80)

era5_files = {
    'initial_state': 'data/era5/era5_initial_state.nc',
    'initial_surface': 'data/era5/era5_initial_surface.nc'
}

for era5_name, filepath in era5_files.items():
    print(f"\n{era5_name}:")
    print(f"  File: {filepath}")
    
    try:
        ds = xr.open_dataset(filepath)
        print(f"  ✓ File exists and readable")
        print(f"  Variables: {', '.join(list(ds.data_vars)[:10])}")
        print(f"  Dimensions: {dict(ds.dims)}")
        
        if 'time' in ds.dims:
            times = ds.time.values
            print(f"  Time range: {pd.Timestamp(times[0])} to {pd.Timestamp(times[-1])}")
            print(f"  Time steps: {len(times)}")
        
        if 'latitude' in ds.dims and 'longitude' in ds.dims:
            print(f"  Lat range: {float(ds.latitude.min()):.2f} to {float(ds.latitude.max()):.2f}")
            print(f"  Lon range: {float(ds.longitude.min()):.2f} to {float(ds.longitude.max()):.2f}")
        
        # Check for wind variables
        wind_vars = [v for v in ds.data_vars if any(x in v.lower() for x in ['u10', 'v10', 'wind'])]
        if wind_vars:
            print(f"  Wind variables: {', '.join(wind_vars)}")
            
        ds.close()
        
    except FileNotFoundError:
        print(f"  ✗ File not found")
    except Exception as e:
        print(f"  ✗ Error reading file: {e}")

# ============================================================================
# 4. CHECK BUOY DATA
# ============================================================================

print("\n" + "=" * 80)
print("4. MARINE BUOY DATA")
print("=" * 80)

buoy_dir = Path('data/Bouy data')
if buoy_dir.exists():
    buoy_files = list(buoy_dir.glob('*.pdf'))
    print(f"\n  Found {len(buoy_files)} PDF files:")
    for bf in buoy_files:
        print(f"    - {bf.name}")
    
    if (buoy_dir / 'buoy_long_lat.png').exists():
        print(f"  ✓ Buoy location map available")
    
    if (buoy_dir / 'buoy_details.txt').exists():
        print(f"  ✓ Buoy details available")
else:
    print("  ✗ Buoy data directory not found")

# ============================================================================
# 5. SUMMARY AND DATA COMPATIBILITY CHECK
# ============================================================================

print("\n" + "=" * 80)
print("SUMMARY & DATA COMPATIBILITY")
print("=" * 80)

print("\n✓ Data inspection complete!")

# Check what's available
has_forecasts = FORECAST_BASE.exists() and any(models.values())
has_stations = any(Path(f).exists() for f in station_files.values())
has_era5 = any(Path(f).exists() for f in era5_files.values())

print("\n📊 Data Availability:")
print(f"  {'✓' if has_forecasts else '✗'} Forecast data (IFS, AIFS)")
print(f"  {'✓' if has_stations else '✗'} Met Éireann stations")
print(f"  {'✓' if has_era5 else '✗'} ERA5 reanalysis")

if has_forecasts:
    print("\n✅ Forecast data found! You can proceed with analysis.")
    print("\nNext steps:")
    print("  1. Verify forecast files contain wind data (u10, v10)")
    print("  2. Check that dates/times align with your analysis period")
    print("  3. Run: jupyter notebook wind_forecast_evaluation.ipynb")
else:
    print("\n⚠️  No forecast data found!")
    print("\nTo download data:")
    print("  1. Run the ECMWF download script")
    print("  2. Wait for downloads to complete")
    print("  3. Run this inspection script again")

print("\n" + "=" * 80)