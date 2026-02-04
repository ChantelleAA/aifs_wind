# AIFS Wind Forecast Evaluation

Comprehensive evaluation of AIFS (ECMWF Artificial Intelligence Forecast System) wind forecasts against observations from Irish weather stations and marine buoys.

## Project Structure

```
aifs_wind/
├── src/aifs_wind/              # Core package modules
│   ├── __init__.py
│   ├── config.py               # Configuration, locations, thresholds
│   └── wind_utils.py           # Data loading & metrics utilities
├── scripts/                     # Executable analysis scripts
│   ├── run_wind_analysis.py     # Main analysis pipeline
│   ├── create_forecast_plots.py # Generate visualization plots
│   ├── download_aifs_ens.py     # Download AIFS ensemble data
│   ├── scrape_ecmwf.py          # Download ECMWF open forecast data
│   ├── extract_buoy_data.py     # Extract marine buoy observations
│   ├── inspect_data.py          # Data structure inspection
│   └── plot_station_map.py      # Generate station location map
├── data/                        # Input data (forecasts, observations)
│   ├── ecmwf_forecasts/         # Downloaded model data
│   ├── Met eireann/             # Station observations
│   ├── Bouy data/               # Marine buoy observations
│   ├── era5/                    # ERA5 reanalysis data
│   └── *.csv                    # Sample data files
├── notebooks/                   # Jupyter notebooks
│   └── wind_forecast_evaluation_updated.ipynb
├── reports/                     # Analysis outputs
│   ├── corrected_results/       # Results CSV files
│   └── *.csv                    # Summary statistics
├── outputs/                     # Generated outputs
│   └── visualizations/          # Figures and plots
├── config/                      # Configuration files
│   └── config.json
├── docs/                        # Documentation
├── presentations/               # Presentation files
├── pyproject.toml              # Package metadata
├── README.MD                    # This file
└── requirements.txt            # Python dependencies
```

## Installation

### Standard Installation

```bash
cd /path/to/aifs_wind
pip install -e .
```

### Development Installation

```bash
pip install -e ".[dev]"
```

## Usage

### Running the Analysis Pipeline

```bash
cd scripts
python run_wind_analysis.py
```

### Downloading Forecast Data

```bash
# Download AIFS ensemble data
python download_aifs_ens.py

# Download ECMWF open data (IFS, AIFS)
python scrape_ecmwf.py
```

### Generating Visualizations

```bash
python create_forecast_plots.py
python plot_station_map.py
```

### Data Inspection

```bash
python inspect_data.py
```

## Data Sources

### Observations
- **Onshore & Coastal**: Met Éireann weather stations
- **Offshore**: Marine Institute buoys (M2-M6)

### Forecasts
- **IFS**: ECMWF Integrated Forecast System
- **AIFS Single**: AIFS deterministic forecast
- **AIFS Ensemble**: AIFS ensemble forecast (51 members)

### Locations Analyzed

| Environment | Name | Type |
|------------|------|------|
| **Onshore** | Shannon Airport, Cork Airport | Station |
| **Coastal** | Malin Head, Valentia, Mace Head, Sherkin Island | Station |
| **Offshore** | M2-M6 Buoys | Marine |

## Key Features

✓ **Proper Time Handling**: Valid time calculation from init + lead time  
✓ **Ensemble Analysis**: Support for 51-member ensemble forecasts  
✓ **Grid Distance Calculation**: Accounts for model grid resolution (~0.25°)  
✓ **Comprehensive Metrics**: Bias, RMSE, MAE, correlation, categorical scores  
✓ **Multi-Environment Evaluation**: Onshore, coastal, offshore comparisons  

## Outputs

- `wind_speed_timeseries.csv` - Model forecasts vs observations
- `verification_metrics.csv` - Performance metrics by location/model
- `ensemble_analysis.csv` - Ensemble-specific statistics
- `forecast_plots.png` - Multi-location comparison visualizations
- `irish_stations_map.png` - Geographic location map

## Configuration

Edit `src/aifs_wind/config.py` to modify:
- Forecast locations
- Lead times for analysis
- Initialization times
- Extreme event thresholds
- Output directories

## Dependencies

See `pyproject.toml` or `requirements.txt` for full list.

Key packages:
- numpy, pandas: Data processing
- matplotlib, seaborn: Visualization
- xarray, cfgrib: GRIB data handling
- cartopy: Geographic mapping
- ecmwf-opendata: Data download

## Author

Chantelle | February 2026

## License

MIT
