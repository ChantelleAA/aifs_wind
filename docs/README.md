# Wind Forecast Evaluation Implementation Guide

## Overview

This implementation provides a complete framework for evaluating wind forecasts from AIFS (AI-Integrated Forecasting System) and IFS (ECMWF Integrated Forecasting System) against ERA5 reanalysis and observational data around Ireland.

## Files Created

### Core Files
1. **wind_forecast_evaluation.ipynb** - Main Jupyter notebook with step-by-step analysis
2. **wind_utils.py** - Utility functions for data loading and metrics computation
3. **config.py** - Configuration file with all parameters
4. **inspect_data.py** - Data inspection script to examine your files
5. **README.md** - This file

## Installation

### Required Python Packages

```bash
pip install numpy pandas xarray matplotlib seaborn cfgrib eccodes netCDF4 --break-system-packages
```

## Quick Start Guide

### Step 1: Organize Your Data

Create the following directory structure:

```
project/
├── data/
│   ├── Met eireann/
│   │   ├── hourly-dublin-pheonixpark/
│   │   │   └── hly175.csv
│   │   ├── hourly-clare-shannonairport/
│   │   │   └── hly518.csv
│   │   └── ... (other stations)
│   ├── Bouy data/
│   │   ├── m2.pdf
│   │   ├── m3.pdf
│   │   └── ... (other buoys)
│   ├── era5/
│   │   ├── era5_initial_state.nc
│   │   └── era5_initial_surface.nc
│   └── forecasts/
│       ├── aifs_single/
│       │   ├── aifs_single_day1.grib2
│       │   ├── aifs_single_day2.grib2
│       │   └── aifs_single_day3.grib2
│       └── ifs/
│           ├── ifs_day1.grib2
│           ├── ifs_day2.grib2
│           └── ifs_day3.grib2
├── wind_forecast_evaluation.ipynb
├── wind_utils.py
├── config.py
└── inspect_data.py
```

### Step 2: Inspect Your Data

Before running the main analysis, understand your data format:

```bash
python inspect_data.py
```

This will:
- Check if all data files exist
- Show the format and structure of each file
- Identify available variables and time ranges
- Report any issues

### Step 3: Adjust Configuration

Edit `config.py` to match your specific needs:

```python
# Modify locations based on your data
LOCATIONS = {
    'Phoenix_Park': {
        'lat': 53.3638,
        'lon': -6.3436,
        'type': 'onshore',
        ...
    },
    ...
}

# Adjust lead times
LEAD_TIMES = [6, 12, 24]  # hours

# Set extreme thresholds
EXTREME_THRESHOLDS = {
    'percentile': 90,
    'gale': 17.2,  # m/s
    ...
}
```

### Step 4: Run the Analysis

Open and run the Jupyter notebook:

```bash
jupyter notebook wind_forecast_evaluation.ipynb
```

Or use JupyterLab:

```bash
jupyter lab wind_forecast_evaluation.ipynb
```

## Analysis Steps Implemented

The notebook implements all 8 steps from your plan:

### Step 1: Location Selection
- **Onshore**: Phoenix Park, Shannon Airport, Cork Airport
- **Coastal**: Malin Head, Valentia, Mace Head, Sherkin Island
- **Offshore**: M2, M3, M4, M5, M6 buoys

### Step 2-3: Data Extraction and Alignment
- Loads forecasts (AIFS, IFS) at fixed locations
- Extracts ERA5 reanalysis
- Loads station observations
- Ensures UTC time alignment
- Verifies 10m height for all measurements
- Converts all to consistent units (m/s)

### Step 4: Wind Speed Computation
- Computes wind speed from u10, v10 components: `ws = sqrt(u² + v²)`
- Computes wind direction
- Creates time series for all models and observations

### Step 5: Extreme Event Definition
- Multiple methods:
  - Percentile-based (e.g., 90th percentile)
  - Absolute thresholds (Beaufort scale)
  - Combined approach
- Local definitions for each location

### Step 6: Deterministic Metrics
For each location and model:
- **Bias**: Mean forecast error
- **MAE**: Mean Absolute Error
- **RMSE**: Root Mean Square Error
- **Correlation**: Pearson correlation coefficient
- **R²**: Coefficient of determination
- **POD**: Probability of Detection (for extremes)
- **FAR**: False Alarm Ratio
- **CSI**: Critical Success Index

### Step 7: Ensemble Analysis (when available)
- Ensemble mean and spread
- Exceedance probabilities
- Brier score for extreme events
- Reliability diagrams
- Spread-error relationships
- CRPS (Continuous Ranked Probability Score)

### Step 8: Environmental Comparison
- Compare metrics across onshore/coastal/offshore
- Identify where each model performs best
- Analyze bias patterns
- Evaluate extreme event detection by environment

## Usage Examples

### Loading Station Data

```python
from wind_utils import DataLoader

# Load Met Éireann station
loader = DataLoader()
phoenix_park = loader.load_met_eireann_station(
    'data/Met eireann/hourly-dublin-pheonixpark/hly175.csv'
)
```

### Loading ERA5 at a Location

```python
era5_data = loader.load_era5_at_location(
    lat=53.3638,
    lon=-6.3436,
    era5_file='data/era5/era5_initial_state.nc'
)
```

### Loading Forecast Data

```python
aifs_data = loader.load_grib_at_location(
    lat=53.3638,
    lon=-6.3436,
    grib_file='data/forecasts/aifs_single/aifs_single_day1.grib2',
    filter_keys={'typeOfLevel': 'heightAboveGround'}
)
```

### Computing Metrics

```python
from wind_utils import ForecastVerification

verifier = ForecastVerification()

# Basic metrics
metrics = verifier.calculate_basic_metrics(
    forecast=aifs_wind_speed,
    observed=obs_wind_speed
)

# Extreme event metrics
extreme_metrics = verifier.calculate_categorical_metrics(
    forecast=aifs_wind_speed,
    observed=obs_wind_speed,
    threshold=17.2  # gale force
)
```

### Defining Extremes

```python
from wind_utils import WindMetrics

wind_metrics = WindMetrics()

# Using percentile method
extreme_mask, threshold = wind_metrics.define_extreme_events(
    wind_speed=observed_wind,
    method='percentile',
    percentile=90
)

# Using absolute threshold
extreme_mask, threshold = wind_metrics.define_extreme_events(
    wind_speed=observed_wind,
    method='absolute',
    threshold=17.2  # Beaufort 8
)
```

## Output Structure

The analysis generates:

### 1. Summary Tables
- Overall performance by model
- Performance by environment type
- Performance by lead time

### 2. Visualizations
- Time series comparisons
- Scatter plots (forecast vs observed)
- Error distributions
- Extreme event detection diagrams
- Environment comparison charts
- Ensemble spread plots

### 3. Statistical Reports
- Comprehensive metrics tables
- Contingency tables for extremes
- Reliability diagrams
- Case study analyses

## Troubleshooting

### Common Issues

**1. "Module not found" errors**
```bash
pip install [missing_module] --break-system-packages
```

**2. GRIB file reading errors**
- Ensure cfgrib is installed: `pip install cfgrib --break-system-packages`
- Check GRIB file integrity
- Verify eccodes is properly installed

**3. NetCDF reading errors**
- Install netCDF4: `pip install netCDF4 --break-system-packages`
- Check file permissions

**4. Date/time parsing issues**
- Check CSV date format in Met Éireann files
- Adjust parsing in `DataLoader.load_met_eireann_station()`

**5. Missing data**
- Use `inspect_data.py` to identify gaps
- Adjust time ranges in config.py
- Consider interpolation for small gaps

### Getting Help

If you encounter issues:
1. Check the error message carefully
2. Review the inspection script output
3. Verify data file formats match expectations
4. Check that coordinates are correct (lat/lon)
5. Ensure time zones are all UTC

## Customization

### Adding New Locations

Edit `config.py`:

```python
LOCATIONS['New_Station'] = {
    'lat': 52.0,
    'lon': -8.0,
    'type': 'onshore',  # or 'coastal' or 'offshore'
    'station_id': 1234,
    'name': 'New Station Name'
}
```

### Changing Lead Times

```python
LEAD_TIMES = [3, 6, 12, 24, 48, 72]  # hours
```

### Adjusting Extreme Thresholds

```python
EXTREME_THRESHOLDS = {
    'percentile': 95,  # top 5% of events
    'severe_gale': 24.5,  # Beaufort 10
    'custom': 20.0  # custom threshold
}
```

### Adding New Metrics

In `wind_utils.py`, add to `ForecastVerification` class:

```python
@staticmethod
def calculate_your_metric(forecast, observed):
    # Your metric calculation
    return metric_value
```

## Performance Considerations

For large datasets:
1. Process locations in parallel (set `use_parallel=True` in config)
2. Reduce time resolution if needed
3. Focus on specific time periods
4. Use data chunking for very large files

## Expected Results

After running the complete analysis, you should have:

1. **Quantitative assessment** of which model (AIFS vs IFS) performs better:
   - Overall
   - By environment type
   - By lead time
   - For extreme events

2. **Understanding of biases**:
   - Does AIFS over/under-predict?
   - How do biases vary by location type?
   - Are biases consistent across lead times?

3. **Extreme event capability**:
   - Which model better detects high winds?
   - What's the false alarm rate?
   - How does ensemble help (if available)?

4. **Environment-specific insights**:
   - Is offshore forecasting harder?
   - Do coastal stations show unique patterns?
   - Where is each model most/least reliable?

## Next Steps After Analysis

1. **Identify patterns**: Look for systematic biases
2. **Case studies**: Deep dive into specific storm events
3. **Seasonal analysis**: Does performance vary by season?
4. **Directional analysis**: Are certain wind directions harder to forecast?
5. **Calibration**: Can forecasts be bias-corrected?
6. **Ensemble weighting**: Optimal combination of models?

## References

### Beaufort Wind Scale
- Force 4 (Moderate breeze): 5.5-8.0 m/s
- Force 6 (Strong breeze): 10.8-13.9 m/s
- Force 8 (Gale): 17.2-20.8 m/s
- Force 10 (Storm): 24.5-28.5 m/s

### Forecast Verification Metrics
- WMO guidelines on forecast verification
- ECMWF IFS documentation
- Standard statistical measures for continuous variables

## Contact

For questions about this implementation, contact the development team or refer to the documentation.

---

**Version**: 1.0  
**Date**: January 2026  
**Author**: Implementation for Chantelle's wind forecast evaluation project
