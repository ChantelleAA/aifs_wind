"""
Configuration file for Wind Forecast Evaluation

Updated to match the ecmwf_forecasts download structure:
  ecmwf_forecasts/
    ├── ifs/oper/date-N/HHz/type-fc/step-NNNh.grib2
    ├── aifs-single/oper/date-N/HHz/type-fc/step-NNNh.grib2
    └── aifs-ens/enfo/date-N/HHz/type-cf|pf/step-NNNh.grib2
"""

import numpy as np
from pathlib import Path
from glob import glob

# ============================================================================
# FILE PATHS
# ============================================================================

# Base data directory
DATA_DIR = Path("data")

# Downloaded forecast data base directory
FORECAST_BASE_DIR = DATA_DIR / "ecmwf_forecasts"  # ← Fixed: add DATA_DIR prefix

# Met Éireann station data (fixed paths)
STATION_DATA = {
    'Shannon_Airport': "data/Met eireann/hourly-clare-shannonairport/hly518.csv",
    'Cork_Airport': "data/Met eireann/hourly-cork-corkairport/hly3904.csv",
    'Malin_Head': "data/Met eireann/hourly-donegal-malinhead/hly1575.csv",
    'Valentia': "data/Met eireann/hourly-kerry-valentia/hly2275.csv",
    'Mace_Head': "data/Met eireann/houryl-galway-macehead/hly275.csv",
    'Sherkin_Island': "data/Met eireann/hourly-cork-sherkin/hly775.csv"
}

# Marine buoy data (fixed paths - note "Bouy" spelling in your directory)
BUOY_DATA = {
    'M2_Buoy': "data/Bouy data/m2_buoy.csv",
    'M3_Buoy': "data/Bouy data/m3_buoy.csv",
    'M4_Buoy': "data/Bouy data/m4_buoy.csv",
    'M5_Buoy': "data/Bouy data/m5_buoy.csv",
    'M6_Buoy': "data/Bouy data/m6_buoy.csv"
}

# ERA5 reanalysis
ERA5_FILES = {
    'initial_state': DATA_DIR / "era5/era5_initial_state.nc",
    'initial_surface': DATA_DIR / "era5/era5_initial_surface.nc"
}

# Model directory structure (matches download script)
MODEL_CONFIGS = {
    'ifs': {
        'path': FORECAST_BASE_DIR / "ifs" / "oper",
        'stream': 'oper',
        'type': 'fc',
        'display_name': 'IFS'
    },
    'aifs_single': {
        'path': FORECAST_BASE_DIR / "aifs-single" / "oper",
        'stream': 'oper',
        'type': 'fc',
        'display_name': 'AIFS Single'
    },
    'aifs_ensemble': {
        'path': FORECAST_BASE_DIR / "aifs-ens" / "enfo",
        'stream': 'enfo',
        'types': ['cf', 'pf'],  # control and perturbed
        'display_name': 'AIFS Ensemble'
    }
}

# Output directory
OUTPUT_DIR = Path(".")
OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

# ============================================================================
# LOCATIONS
# ============================================================================

LOCATIONS = {
    # Onshore locations
    'Shannon_Airport': {
        'lat': 52.7019,
        'lon': -8.9248,
        'type': 'onshore',
        'station_id': 518,
        'name': 'Shannon Airport'
    },
    'Cork_Airport': {
        'lat': 51.8413,
        'lon': -8.4911,
        'type': 'onshore',
        'station_id': 3904,
        'name': 'Cork Airport'
    },
    
    # Coastal locations
    'Malin_Head': {
        'lat': 55.3697,
        'lon': -7.3386,
        'type': 'coastal',
        'station_id': 1575,
        'name': 'Malin Head, Donegal'
    },
    'Valentia': {
        'lat': 51.9386,
        'lon': -10.2431,
        'type': 'coastal',
        'station_id': 2275,
        'name': 'Valentia Observatory, Kerry'
    },
    'Mace_Head': {
        'lat': 53.3264,
        'lon': -9.9039,
        'type': 'coastal',
        'station_id': 275,
        'name': 'Mace Head, Galway'
    },
    'Sherkin_Island': {
        'lat': 51.4786,
        'lon': -9.4283,
        'type': 'coastal',
        'station_id': 775,
        'name': 'Sherkin Island, Cork'
    },
    
    # Offshore locations (Marine buoys) - CORRECTED COORDINATES FROM PDFs
    'M2_Buoy': {
        'lat': 53.4836,
        'lon': -5.4302,
        'type': 'offshore',
        'buoy_id': 'M2',
        'name': 'M2 Buoy (Irish Sea)'
    },
    'M3_Buoy': {
        'lat': 51.2160,
        'lon': -10.5483,
        'type': 'offshore',
        'buoy_id': 'M3',
        'name': 'M3 Buoy (Celtic Sea)'
    },
    'M4_Buoy': {
        'lat': 55.0000,
        'lon': -10.0000,
        'type': 'offshore',
        'buoy_id': 'M4',
        'name': 'M4 Buoy (Atlantic Northwest)'
    },
    'M5_Buoy': {
        'lat': 51.6904,
        'lon': -6.7043,
        'type': 'offshore',
        'buoy_id': 'M5',
        'name': 'M5 Buoy (Celtic Sea South)'
    },
    'M6_Buoy': {
        'lat': 53.0748,
        'lon': -15.8814,
        'type': 'offshore',
        'buoy_id': 'M6',
        'name': 'M6 Buoy (Deep Atlantic)'
    }
}

# ============================================================================
# ANALYSIS PARAMETERS
# ============================================================================

# Lead times to evaluate (hours) - matches download script
LEAD_TIMES = [6, 12, 24]

# Initialization times (matches download script)
INIT_TIMES = ['00z', '06z', '12z', '18z']

# Extreme event thresholds
EXTREME_THRESHOLDS = {
    'percentile': 90,  # 90th percentile
    'gale': 17.2,      # Beaufort 8 (gale force)
    'strong_gale': 20.8,  # Beaufort 9
    'storm': 24.5      # Beaufort 10
}

# Wind speed thresholds (m/s) based on Beaufort scale
WIND_CATEGORIES = {
    'light': (0, 5.5),      # Forces 0-3
    'moderate': (5.5, 10.8),  # Forces 4-5
    'strong': (10.8, 17.2),   # Forces 6-7
    'gale': (17.2, 24.5),     # Forces 8-9
    'storm': (24.5, 32.7),    # Forces 10-11
    'hurricane': (32.7, np.inf)  # Force 12
}

# ============================================================================
# FORECAST MODEL PARAMETERS
# ============================================================================

# Models to evaluate
MODELS = ['IFS', 'AIFS-Single', 'AIFS-Ensemble']

# Ensemble settings
ENSEMBLE_SETTINGS = {
    'n_members': 51,  # CORRECTED: 1 control + 50 perturbed = 51 total
    'use_ensemble': True,  # Set to True to include ensemble analysis
    'ensemble_types': ['cf', 'pf']  # control forecast, perturbed forecast
}

# ============================================================================
# VERIFICATION METRICS
# ============================================================================

# Which metrics to calculate
METRICS_TO_CALCULATE = {
    'basic': True,      # Bias, MAE, RMSE, correlation
    'categorical': True,  # POD, FAR, CSI for extremes
    'ensemble': True,   # Ensemble-specific metrics
    'temporal': True     # Time-of-day, seasonal variations
}

# ============================================================================
# PLOTTING PARAMETERS
# ============================================================================

PLOT_SETTINGS = {
    'figsize': (12, 6),
    'dpi': 100,
    'style': 'seaborn-v0_8-darkgrid',
    'color_palette': 'husl',
    'save_format': 'png'
}

# Colors for different environments
ENVIRONMENT_COLORS = {
    'onshore': '#1f77b4',   # Blue
    'coastal': '#ff7f0e',   # Orange
    'offshore': '#2ca02c'   # Green
}

# Colors for different models
MODEL_COLORS = {
    'AIFS-Single': '#e74c3c',  # Red
    'AIFS-Ensemble': '#9b59b6', # Purple
    'IFS': '#3498db',          # Blue
    'ERA5': '#2ecc71',         # Green
    'Observed': '#34495e'      # Dark gray
}

# ============================================================================
# DATA QUALITY CONTROL
# ============================================================================

# Quality control thresholds
QC_THRESHOLDS = {
    'max_wind_speed': 50.0,  # m/s - physically unrealistic above this
    'min_wind_speed': 0.0,   # m/s
    'max_missing_pct': 20,   # % - discard locations with more missing data
}

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def get_forecast_files(model_key, date_offset=-1, init_time='00z', lead_time=12):
    """
    Get forecast file path for a specific model, date, time, and lead time.
    
    Parameters:
    -----------
    model_key : str
        One of 'ifs', 'aifs_single', 'aifs_ensemble'
    date_offset : int
        Days back from today (0=today, -1=yesterday, -2=day before, etc.)
    init_time : str
        Initialization time: '00z', '06z', '12z', or '18z'
    lead_time : int
        Forecast lead time in hours (e.g., 6, 12, 24)
    
    Returns:
    --------
    Path or list of Paths
        For deterministic: single Path
        For ensemble: list of Paths [control, perturbed_members...]
    """
    if model_key not in MODEL_CONFIGS:
        raise ValueError(f"Unknown model: {model_key}")
    
    config = MODEL_CONFIGS[model_key]
    base_path = config['path']
    
    # Construct path: model/stream/date{offset}/HHz/type-XX/step-NNNh.grib2
    date_dir = f"date{date_offset:+d}"  # e.g., "date-1" for yesterday
    time_dir = init_time  # e.g., "00z"
    step_file = f"step-{lead_time:03d}h.grib2"  # e.g., "step-012h.grib2"
    
    if model_key == 'aifs_ensemble':
        # Return both control and perturbed forecast files
        files = []
        for ftype in config['types']:
            type_dir = f"type-{ftype}"
            file_path = base_path / date_dir / time_dir / type_dir / step_file
            if file_path.exists():
                files.append(file_path)
        return files if files else None
    else:
        # Deterministic forecast
        type_dir = f"type-{config['type']}"
        file_path = base_path / date_dir / time_dir / type_dir / step_file
        return file_path if file_path.exists() else None

def list_available_dates():
    """
    List all available dates across all models.
    
    Returns:
    --------
    list of str
        Date directories found (e.g., ['date+0', 'date-1', 'date-2'])
    """
    dates = set()
    for model_key, config in MODEL_CONFIGS.items():
        base_path = config['path']
        if base_path.exists():
            for date_dir in base_path.iterdir():
                if date_dir.is_dir() and date_dir.name.startswith('date'):
                    dates.add(date_dir.name)
    return sorted(dates)

def list_available_times(model_key, date_offset):
    """
    List available initialization times for a given model and date.
    """
    if model_key not in MODEL_CONFIGS:
        return []
    
    config = MODEL_CONFIGS[model_key]
    base_path = config['path']
    date_dir = f"date{date_offset:+d}"
    
    date_path = base_path / date_dir
    if not date_path.exists():
        return []
    
    times = []
    for time_dir in date_path.iterdir():
        if time_dir.is_dir() and time_dir.name.endswith('z'):
            times.append(time_dir.name)
    
    return sorted(times)

def list_available_lead_times(model_key, date_offset, init_time):
    """
    List available lead times for a given model, date, and init time.
    """
    if model_key not in MODEL_CONFIGS:
        return []
    
    config = MODEL_CONFIGS[model_key]
    base_path = config['path']
    date_dir = f"date{date_offset:+d}"
    
    # For deterministic
    if model_key != 'aifs_ensemble':
        type_dir = f"type-{config['type']}"
        step_path = base_path / date_dir / init_time / type_dir
    else:
        # For ensemble, check control forecast
        type_dir = "type-cf"
        step_path = base_path / date_dir / init_time / type_dir
    
    if not step_path.exists():
        return []
    
    lead_times = []
    for step_file in step_path.glob("step-*.grib2"):
        # Extract lead time from filename: step-012h.grib2 -> 12
        try:
            lead_time = int(step_file.stem.split('-')[1].replace('h', ''))
            lead_times.append(lead_time)
        except (IndexError, ValueError):
            continue
    
    return sorted(lead_times)

# ============================================================================
# REPORTING
# ============================================================================

# Report settings
REPORT_SETTINGS = {
    'generate_summary_table': True,
    'generate_location_reports': True,
    'generate_comparison_plots': True,
    'generate_case_studies': False,  # Set True for specific events
    'decimal_places': 3
}

# ============================================================================
# COMPUTATIONAL SETTINGS
# ============================================================================

# Parallel processing (if needed for large datasets)
COMPUTATIONAL = {
    'use_parallel': False,
    'n_workers': 4
}

if __name__ == "__main__":
    print("Configuration loaded successfully")
    print(f"\nForecast base directory: {FORECAST_BASE_DIR}")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"\nLocations: {len(LOCATIONS)}")
    print(f"  Onshore: {sum(1 for loc in LOCATIONS.values() if loc['type'] == 'onshore')}")
    print(f"  Coastal: {sum(1 for loc in LOCATIONS.values() if loc['type'] == 'coastal')}")
    print(f"  Offshore: {sum(1 for loc in LOCATIONS.values() if loc['type'] == 'offshore')}")
    print(f"\nLead times: {LEAD_TIMES} hours")
    print(f"Init times: {INIT_TIMES}")
    print(f"Models: {MODELS}")
    
    # Show what data is available
    print(f"\n{'='*60}")
    print("Available Data:")
    print(f"{'='*60}")
    dates = list_available_dates()
    if dates:
        print(f"Date offsets found: {dates}")
        for model_key in MODEL_CONFIGS.keys():
            print(f"\n{MODEL_CONFIGS[model_key]['display_name']}:")
            for date in dates:
                date_offset = int(date.replace('date', ''))
                times = list_available_times(model_key, date_offset)
                print(f"  {date}: {times if times else 'No data'}")
    else:
        print("No forecast data found. Run the download script first!")