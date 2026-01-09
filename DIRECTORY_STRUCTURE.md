# Directory Structure

## Overview
Organized wind model comparison project with separated data, notebooks, documentation, and outputs.

## Directory Layout

### `/data/` - All weather and model data (337 MB)

#### `/data/forecasts/` - Model forecast data
- **`ifs/`** - IFS (Integrated Forecasting System) multi-day forecasts
  - `ifs_day1.grib2` (47 MB) - Day 1 forecast
  - `ifs_day2.grib2` (46 MB) - Day 2 forecast  
  - `ifs_day3.grib2` (46 MB) - Day 3 forecast

- **`aifs_single/`** - AIFS-Single (AI deterministic) multi-day forecasts
  - `aifs_single_day1.grib2` (38 MB) - Day 1 forecast
  - `aifs_single_day2.grib2` (38 MB) - Day 2 forecast

#### `/data/observations/` - Verification and analysis data
- `ifs_winds.grib2` (9.0 MB) - IFS 10m wind components subset
- `aifs_single_winds.grib2` (4.1 MB) - AIFS-Single 10m wind components subset
- `analysis_winds.grib2` (1.7 MB) - Analysis/observation wind verification data
- `ecmwf_ifs_data.grib2` (21 MB) - Additional ECMWF IFS data (backup)
- `data.grib2` (642 KB) - Miscellaneous analysis data

#### `/data/era5/` - ERA5 reanalysis initialization data
- `era5_initial_state.nc` (81 MB) - ERA5 initial state 3D atmospheric fields
- `era5_initial_surface.nc` (8.0 MB) - ERA5 surface fields

#### `/data/indices/` - GRIB index files
- `ifs_winds.grib2.5b7b6.idx` - Index for IFS wind data
- `aifs_single_winds.grib2.5b7b6.idx` - Index for AIFS-Single wind data
- `analysis_winds.grib2.5b7b6.idx` - Index for analysis wind data

---

### `/notebooks/` - Jupyter analysis and exploration (572 KB)

#### `/notebooks/analysis/` - Primary analysis workflow
- `wind_analysis.ipynb` - **Complete 15-step analysis pipeline**
  - STEP 1-3: Setup, configuration, initialization
  - STEP 4-7: Data loading and extraction
  - STEP 8-10: Statistical comparison and bias analysis
  - STEP 11-14: Comprehensive visualizations
  - STEP 15: Summary report generation

#### `/notebooks/exploratory/` - Exploratory development
- `aifs1.ipynb` - Initial methodology and exploration
- `aifs2.ipynb` - Additional exploration and testing

#### `/notebooks/reference/` - Reference implementations
- `run_AIFS_v1.ipynb` - AIFS model inference and testing

---

### `/docs/` - Documentation and configuration (28 KB)

- `README.md` - Project overview
- `ANALYSIS_GUIDE.md` - Detailed analysis methodology and interpretation guide
- `requirements.txt` - Python package dependencies
- `pip_install.log` - Package installation log

---

### `/outputs/` - Generated outputs and results (164 KB)

#### `/outputs/visualizations/`
- `wind_comparison.png` - Visualization of wind model comparison

---

## File Size Summary
```
data/              337 MB  (weather model and reanalysis data)
notebooks/         572 KB  (Jupyter analysis notebooks)
docs/               28 KB  (documentation)
outputs/           164 KB  (generated visualizations)
─────────────────────────
Total:             338 MB
```

## Usage

### To Run Analysis
1. Open and execute: `notebooks/analysis/wind_analysis.ipynb`
2. This notebook loads data from `data/forecasts/` and `data/observations/`
3. Generates outputs to `outputs/visualizations/`

### To Reference Methodology
- See: `docs/ANALYSIS_GUIDE.md` for detailed methodology
- See: `notebooks/exploratory/aifs1.ipynb` for methodology notes

### To Understand Data
- **Forecasts**: 6-7 day forecasts from two model systems
- **Observations**: Wind speed verification/analysis data  
- **ERA5**: Reanalysis initial conditions for model initialization

## Data Sources
- **IFS & AIFS**: ECMWF Open Data API
- **ERA5**: ECMWF Copernicus Climate Data Store
- **Analysis data**: Local processing from observations

## Models Compared
- **IFS** (Integrated Forecasting System) - Traditional physics-based
- **AIFS-Single** (AI Integrated Forecasting System - Deterministic) - AI-based deterministic forecasts
- **AIFS-Ensemble** (AI Integrated Forecasting System - Ensemble) - AI-based ensemble predictions

## Analysis Parameters
- **Duration**: 7 days
- **Lead times**: 24, 48, 72, 96, 120, 144 hours
- **Wind variables**: 10m (u, v), 100m (u, v), gusts
- **High wind threshold**: 12.5 m/s
