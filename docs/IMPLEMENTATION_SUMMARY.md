# Wind Forecast Evaluation - Implementation Summary

## What Has Been Created

I've implemented a complete framework for evaluating wind forecasts (AIFS vs IFS) around Ireland. Here's what you have:

### Core Implementation Files

1. **wind_forecast_evaluation.ipynb**
   - Main Jupyter notebook with step-by-step implementation
   - Implements all 8 steps from your analysis plan
   - Ready to run once you have your data files

2. **wind_utils.py** 
   - Python module with reusable utility functions
   - Classes: DataLoader, WindMetrics, ForecastVerification
   - Functions for loading ERA5, GRIB2, station data
   - Complete metrics calculation suite

3. **config.py**
   - Central configuration file
   - All locations (onshore, coastal, offshore)
   - Analysis parameters (lead times, thresholds)
   - Easy to modify without changing code

4. **inspect_data.py**
   - Data inspection script
   - Run this FIRST to understand your data
   - Checks file formats and availability

5. **example_workflow.py**
   - Complete example showing the full workflow
   - Demonstrates every step of the analysis
   - Template you can adapt

6. **README.md**
   - Comprehensive documentation
   - Installation instructions
   - Usage examples
   - Troubleshooting guide

### Demo Output

I've also created a demonstration using synthetic data:
- **example_forecast_evaluation.png** - Shows what your final plots will look like

## How It Implements Your 8-Step Plan

### ✓ Step 1: Location Selection
```python
# Defined in config.py
LOCATIONS = {
    'Phoenix_Park': {'lat': 53.36, 'lon': -6.34, 'type': 'onshore'},
    'Malin_Head': {'lat': 55.37, 'lon': -7.34, 'type': 'coastal'},
    'M2_Buoy': {'lat': 53.49, 'lon': -5.43, 'type': 'offshore'},
    # ... 12 locations total
}
```

### ✓ Step 2: Extract Historical Forecasts
```python
# In wind_utils.py
loader = DataLoader()
aifs_data = loader.load_grib_at_location(lat, lon, 'aifs_file.grib2')
ifs_data = loader.load_grib_at_location(lat, lon, 'ifs_file.grib2')
era5_data = loader.load_era5_at_location(lat, lon, 'era5_file.nc')
```

### ✓ Step 3: Consistent Alignment
- All timestamps converted to UTC
- Height standardized to 10m
- Units standardized to m/s
- Implemented in data loading functions

### ✓ Step 4: Compute Wind Speed
```python
# In wind_utils.py
wind_metrics = WindMetrics()
wind_speed = wind_metrics.compute_wind_speed(u10, v10)
wind_direction = wind_metrics.compute_wind_direction(u10, v10)
```

### ✓ Step 5: Define Extreme Events
```python
# Multiple methods available
extreme_mask, threshold = wind_metrics.define_extreme_events(
    wind_speed,
    method='percentile',  # or 'absolute' or 'both'
    percentile=90
)
```

### ✓ Step 6: Deterministic Metrics
```python
verifier = ForecastVerification()
metrics = verifier.calculate_basic_metrics(forecast, observed)
# Returns: bias, MAE, RMSE, correlation, R²

extreme_metrics = verifier.calculate_categorical_metrics(
    forecast, observed, threshold
)
# Returns: POD, FAR, CSI, hits, misses, false alarms
```

### ✓ Step 7: Ensemble Analysis
```python
ensemble_metrics = verifier.calculate_ensemble_metrics(
    ensemble_members,  # shape: (n_members, n_times)
    observed,
    threshold=17.2
)
# Returns: spread, CRPS, Brier score, exceedance probabilities
```

### ✓ Step 8: Environmental Comparison
```python
# Functions to compare across environments
summary = compare_environments(results_by_location, locations_df)
# Analyzes onshore vs coastal vs offshore performance
```

## What You Need to Do Next

### Immediate Steps

1. **Upload Your Data Files**
   ```
   Place files in this structure:
   data/
   ├── Met eireann/
   │   ├── hourly-dublin-pheonixpark/hly175.csv
   │   └── ... (other stations)
   ├── era5/
   │   ├── era5_initial_state.nc
   │   └── era5_initial_surface.nc
   └── forecasts/
       ├── aifs_single/
       │   ├── aifs_single_day1.grib2
       │   └── ...
       └── ifs/
           ├── ifs_day1.grib2
           └── ...
   ```

2. **Run the Inspection Script**
   ```bash
   python inspect_data.py
   ```
   This will tell you:
   - If files are readable
   - What format they're in
   - What variables are available
   - Date ranges covered

3. **Adjust Configuration**
   - Open `config.py`
   - Verify locations are correct
   - Set your desired lead times
   - Adjust extreme event thresholds if needed

4. **Run the Analysis**
   ```bash
   jupyter notebook wind_forecast_evaluation.ipynb
   ```
   Or run cells one by one to see results progressively

### If Data Files Have Different Formats

If your files don't match the expected format, you'll need to adjust the loading functions in `wind_utils.py`:

**For Met Éireann station data:**
```python
# In DataLoader.load_met_eireann_station()
# Adjust column names, date parsing, etc.
```

**For ERA5:**
```python
# In DataLoader.load_era5_at_location()
# Adjust variable names, coordinate systems
```

**For GRIB files:**
```python
# In DataLoader.load_grib_at_location()
# Adjust filter_keys, variable names
```

### For Buoy Data (PDFs)

The buoy data in PDF format will need special handling:
```python
# You may need to:
1. Extract data from PDFs (use PyPDF2 or pdfplumber)
2. Or manually export data to CSV
3. Then load with custom function
```

## Understanding the Output

### Metrics Explained

**Basic Metrics:**
- **Bias**: Mean error (positive = over-forecast, negative = under-forecast)
- **MAE**: Mean Absolute Error (typical magnitude of errors)
- **RMSE**: Root Mean Square Error (penalizes large errors more)
- **Correlation**: How well forecast captures variability (0-1)
- **R²**: Explained variance (0-1)

**Extreme Event Metrics:**
- **POD** (Probability of Detection): What fraction of extremes were forecast? (0-1, higher better)
- **FAR** (False Alarm Ratio): What fraction of forecasts were wrong? (0-1, lower better)
- **CSI** (Critical Success Index): Overall skill (0-1, higher better)

**Ensemble Metrics:**
- **Spread**: Ensemble uncertainty
- **CRPS**: Overall probabilistic skill (lower better)
- **Brier Score**: Probability forecast skill (lower better)

### What Good Results Look Like

**For Deterministic Forecasts:**
- RMSE: < 2 m/s is good, < 1.5 m/s is excellent
- Correlation: > 0.85 is good, > 0.90 is excellent
- Bias: Close to 0 (within ±0.5 m/s)
- POD: > 0.70 for extremes
- FAR: < 0.30 for extremes

**For Ensemble Forecasts:**
- Spread should match error (ratio near 1.0)
- CRPS should be less than RMSE of ensemble mean
- Brier score < 0.15 is good for extremes

## Expected Findings

Based on similar studies, you might find:

1. **AIFS typically shows:**
   - Competitive or better accuracy than IFS
   - Sometimes smoother forecasts (less variability)
   - May have different biases in different environments

2. **Environmental differences:**
   - Offshore often has larger errors (less observational data)
   - Coastal can be tricky (land-sea interactions)
   - Onshore typically most accurate

3. **Lead time degradation:**
   - Skill decreases with lead time
   - RMSE typically increases by ~0.5 m/s per day

4. **Extreme events:**
   - Harder to forecast than mean winds
   - Higher false alarm rates
   - Ensemble can help quantify uncertainty

## Troubleshooting Common Issues

### "Module not found"
```bash
pip install [module_name] --break-system-packages
```

### "Cannot read GRIB file"
- Check cfgrib is installed
- Verify file isn't corrupted
- Check file permissions

### "Date parsing error"
- Check CSV format in inspect script output
- Adjust date parsing in DataLoader

### "Coordinates not found"
- ERA5 uses 0-360° longitude (not -180 to 180)
- Code handles this, but verify coordinates

### "No data at location"
- Check if lat/lon are within data domain
- Use nearest neighbor (already implemented)

## Advanced Usage

### Running for All Locations

```python
results = {}
for loc_name, loc_info in LOCATIONS.items():
    print(f"Processing {loc_name}...")
    # Load data, compute metrics
    results[loc_name] = metrics

# Then compare
summary = compare_environments(results, locations_df)
```

### Analyzing Different Time Periods

```python
# In config.py
ANALYSIS_PERIOD = {
    'start': '2024-01-01',
    'end': '2024-01-31',  # Just January
    'frequency': 'H'
}
```

### Custom Thresholds

```python
# Define your own
CUSTOM_THRESHOLDS = {
    'light_wind': 5.0,
    'strong_wind': 15.0,
    'very_strong': 20.0
}
```

## Files Provided

All files are in `./`:

1. wind_forecast_evaluation.ipynb - Main analysis notebook
2. wind_utils.py - Utility functions
3. config.py - Configuration
4. inspect_data.py - Data inspection
5. example_workflow.py - Complete example
6. README.md - Documentation
7. IMPLEMENTATION_SUMMARY.md - This file
8. example_forecast_evaluation.png - Demo visualization

## Final Notes

This implementation provides:
- ✓ Complete workflow for all 8 steps
- ✓ Flexible configuration
- ✓ Comprehensive metrics
- ✓ Clear visualizations
- ✓ Extensible design

**You're ready to:**
1. Add your data files
2. Run the inspection
3. Execute the analysis
4. Get results comparing AIFS vs IFS

**The framework handles:**
- Multiple locations
- Multiple models
- Multiple lead times
- Extreme event analysis
- Environmental comparisons

Good luck with your analysis! The implementation is complete and ready for your data.

---

**Questions?** Review README.md for detailed usage examples and troubleshooting.
