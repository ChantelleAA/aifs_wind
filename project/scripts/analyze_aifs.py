#!/usr/bin/env python3
"""
Analyze AIFS forecasts: Single deterministic vs Ensemble spread
Extracts 10m wind at M2 buoy location and creates 3 comparison plots
"""

import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Configuration
DATA_DIR = Path("/home/chantelle/Desktop/PhD Project/code/aifs_wind/project/data/ecmwf_forecasts")
OUTPUT_DIR = Path("/home/chantelle/Desktop/PhD Project/code/aifs_wind/project/plots")
OUTPUT_DIR.mkdir(exist_ok=True)

# M2 Buoy location (offshore)
STATION_LAT = 53.48
STATION_LON = -5.425
STATION_NAME = "M2 Buoy"

# Analysis setup
INIT_DATE = "20260209"  # Feb 9, 2026
INIT_TIME = "00z"
LEAD_TIMES = [0, 6, 12, 24, 48, 72, 96, 120, 144]  # hours

print("="*80)
print(f"AIFS Wind Analysis for {STATION_NAME}")
print(f"Init: {INIT_DATE} {INIT_TIME}")
print(f"Location: {STATION_LAT}°N, {STATION_LON}°E")
print("="*80)

def read_grib_wind(filepath, lat, lon):
    """Extract 10u and 10v wind components at nearest grid point"""
    try:
        ds = xr.open_dataset(filepath, engine='cfgrib')
        
        # Find nearest grid point
        ds_point = ds.sel(latitude=lat, longitude=lon, method='nearest')
        
        # Get wind components
        u = ds_point['u10'].values if 'u10' in ds_point else None
        v = ds_point['v10'].values if 'v10' in ds_point else None
        
        if u is not None and v is not None:
            # Calculate wind speed
            speed = np.sqrt(u**2 + v**2)
            return float(speed)
        return None
    except Exception as e:
        print(f"Error reading {filepath.name}: {e}")
        return None

# ============================================================================
# 1. AIFS-SINGLE: Deterministic forecast evolution
# ============================================================================
print("\n1. Reading AIFS-Single data...")
single_winds = []
single_times = []

for step in LEAD_TIMES:
    filepath = DATA_DIR / "aifs-single" / "oper" / f"date{INIT_DATE}" / INIT_TIME / "type-fc" / "levtype-sfc" / f"step-{step:03d}h.grib2"
    
    if filepath.exists():
        wind = read_grib_wind(filepath, STATION_LAT, STATION_LON)
        if wind is not None:
            single_winds.append(wind)
            # Calculate valid time
            init_dt = datetime.strptime(INIT_DATE + INIT_TIME[:2], "%Y%m%d%H")
            valid_dt = init_dt + timedelta(hours=step)
            single_times.append(valid_dt)
            print(f"  Step {step:03d}h: {wind:.2f} m/s (valid: {valid_dt})")
    else:
        print(f"  Step {step:03d}h: FILE NOT FOUND")

print(f"\nAIFS-Single: {len(single_winds)} points")

# ============================================================================
# 2. AIFS-ENS: Ensemble members (cf + pf)
# ============================================================================
print("\n2. Reading AIFS-ENS data...")

# Control member (cf)
ens_cf_winds = []
ens_cf_times = []

for step in LEAD_TIMES:
    filepath = DATA_DIR / "aifs-ens" / "enfo" / f"date{INIT_DATE}" / INIT_TIME / "type-cf" / "levtype-sfc" / f"step-{step:03d}h.grib2"
    
    if filepath.exists():
        wind = read_grib_wind(filepath, STATION_LAT, STATION_LON)
        if wind is not None:
            ens_cf_winds.append(wind)
            init_dt = datetime.strptime(INIT_DATE + INIT_TIME[:2], "%Y%m%d%H")
            valid_dt = init_dt + timedelta(hours=step)
            ens_cf_times.append(valid_dt)

print(f"Ensemble control: {len(ens_cf_winds)} points")

# Perturbed members (pf) - all 50 members
ens_pf_winds = {step: [] for step in LEAD_TIMES}
ens_pf_times = []

for step in LEAD_TIMES:
    filepath = DATA_DIR / "aifs-ens" / "enfo" / f"date{INIT_DATE}" / INIT_TIME / "type-pf" / "levtype-sfc" / f"step-{step:03d}h.grib2"
    
    if filepath.exists():
        try:
            ds = xr.open_dataset(filepath, engine='cfgrib')
            ds_point = ds.sel(latitude=STATION_LAT, longitude=STATION_LON, method='nearest')
            
            # PF files contain all 50 members
            if 'number' in ds_point.dims:
                for member in ds_point['number'].values:
                    ds_member = ds_point.sel(number=member)
                    u = ds_member['u10'].values
                    v = ds_member['v10'].values
                    speed = float(np.sqrt(u**2 + v**2))
                    ens_pf_winds[step].append(speed)
            
            init_dt = datetime.strptime(INIT_DATE + INIT_TIME[:2], "%Y%m%d%H")
            valid_dt = init_dt + timedelta(hours=step)
            if step == LEAD_TIMES[0]:  # Only add times once
                ens_pf_times.append(valid_dt)
        except Exception as e:
            print(f"  Step {step:03d}h pf: {e}")

print(f"Perturbed members: {sum(len(v) for v in ens_pf_winds.values())} total values")

# ============================================================================
# 3. CREATE PLOTS
# ============================================================================

fig, axes = plt.subplots(3, 1, figsize=(14, 12))
fig.suptitle(f'AIFS Wind Forecasts for {STATION_NAME}\n'
             f'Init: {INIT_DATE} {INIT_TIME}', 
             fontsize=16, fontweight='bold')

# -------------------------
# PLOT 1: AIFS-Single only
# -------------------------
ax = axes[0]
if single_winds:
    ax.plot(single_times, single_winds, 'b-o', linewidth=2, markersize=8, label='AIFS-Single')
    ax.set_ylabel('10m Wind Speed (m/s)', fontsize=12)
    ax.set_title('AIFS-Single: Deterministic Forecast Evolution', fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=11)
else:
    ax.text(0.5, 0.5, 'No AIFS-Single data', ha='center', va='center', transform=ax.transAxes)

# -------------------------
# PLOT 2: AIFS-ENS spread
# -------------------------
ax = axes[1]
if ens_cf_winds:
    # Plot all perturbed members
    for step_idx, step in enumerate(LEAD_TIMES):
        if ens_pf_winds[step]:
            valid_dt = ens_cf_times[step_idx] if step_idx < len(ens_cf_times) else None
            if valid_dt:
                # Plot all 50 members at this timestep
                for member_wind in ens_pf_winds[step]:
                    ax.scatter(valid_dt, member_wind, c='lightcoral', s=20, alpha=0.3, zorder=1)
    
    # Plot control member on top
    ax.plot(ens_cf_times, ens_cf_winds, 'r-o', linewidth=2, markersize=8, 
            label='Control (cf)', zorder=3)
    
    ax.set_ylabel('10m Wind Speed (m/s)', fontsize=12)
    ax.set_title(f'AIFS-ENS: Ensemble Spread (1 control + 50 perturbed members)', 
                 fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=11)
else:
    ax.text(0.5, 0.5, 'No AIFS-ENS data', ha='center', va='center', transform=ax.transAxes)

# -------------------------
# PLOT 3: Comparison
# -------------------------
ax = axes[2]
if single_winds and ens_cf_winds:
    # Single
    ax.plot(single_times, single_winds, 'b-o', linewidth=2, markersize=8, 
            label='AIFS-Single (deterministic)', zorder=3)
    
    # Ensemble mean and spread
    ens_means = []
    ens_stds = []
    for step_idx, step in enumerate(LEAD_TIMES):
        if ens_pf_winds[step] and step_idx < len(ens_cf_winds):
            all_members = ens_pf_winds[step] + [ens_cf_winds[step_idx]]
            ens_means.append(np.mean(all_members))
            ens_stds.append(np.std(all_members))
        else:
            ens_means.append(None)
            ens_stds.append(None)
    
    # Filter out None values
    valid_indices = [i for i, m in enumerate(ens_means) if m is not None]
    valid_times = [ens_cf_times[i] for i in valid_indices if i < len(ens_cf_times)]
    valid_means = [ens_means[i] for i in valid_indices]
    valid_stds = [ens_stds[i] for i in valid_indices]
    
    if valid_means:
        # Ensemble mean
        ax.plot(valid_times, valid_means, 'r-s', linewidth=2, markersize=8,
                label='AIFS-ENS mean', zorder=3)
        
        # Ensemble spread (±1 std)
        ax.fill_between(valid_times,
                        [m - s for m, s in zip(valid_means, valid_stds)],
                        [m + s for m, s in zip(valid_means, valid_stds)],
                        alpha=0.3, color='red', label='AIFS-ENS ±1σ', zorder=1)
    
    ax.set_xlabel('Valid Time (UTC)', fontsize=12)
    ax.set_ylabel('10m Wind Speed (m/s)', fontsize=12)
    ax.set_title('Comparison: Single vs Ensemble', fontsize=13, fontweight='bold')
    ax.grid(True, alpha=0.3)
    ax.legend(fontsize=11)
else:
    ax.text(0.5, 0.5, 'Incomplete data for comparison', 
            ha='center', va='center', transform=ax.transAxes)

# Format x-axis for all plots
for ax in axes:
    ax.tick_params(axis='x', rotation=45)
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')

plt.tight_layout()

# Save
output_file = OUTPUT_DIR / f"aifs_comparison_{INIT_DATE}_{INIT_TIME}_{STATION_NAME.replace(' ', '_')}.png"
plt.savefig(output_file, dpi=300, bbox_inches='tight')
print(f"\n✓ Plot saved: {output_file}")

plt.show()

# ============================================================================
# SUMMARY STATS
# ============================================================================
print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print(f"AIFS-Single:   {len(single_winds)} timesteps")
print(f"  Mean wind:   {np.mean(single_winds):.2f} m/s" if single_winds else "  No data")
print(f"  Max wind:    {np.max(single_winds):.2f} m/s" if single_winds else "")

print(f"\nAIFS-ENS:      {len(ens_cf_winds)} timesteps")
if ens_cf_winds:
    all_ens_winds = []
    for step in LEAD_TIMES:
        all_ens_winds.extend(ens_pf_winds[step])
    print(f"  Total members: {len(all_ens_winds)}")
    print(f"  Mean wind:   {np.mean(all_ens_winds):.2f} m/s")
    print(f"  Spread (std): {np.std(all_ens_winds):.2f} m/s")

print("="*80)
print("✓ Analysis complete!")