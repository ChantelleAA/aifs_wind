# Complete File Structure - AIFS Wind Project

## Project Root Directory
```
/home/chantelle/Desktop/PhD Project/code/aifs_wind/
```

---

## Root Level Files

### Configuration & Documentation Files
```
.git/                                    # Git version control directory
.gitignore                              # Git ignore configuration
config.json                             # Configuration file with stations and parameters
implementation_guide.md                 # Step-by-step implementation guide
roadmap description.md                  # Project roadmap and methodology
DIRECTORY_STRUCTURE.md                  # Directory structure documentation
COMPLETE_FILE_STRUCTURE.md              # This file
```

---

## Directory Structure with Full Contents

### /data/ - Weather Model and Reanalysis Data (337 MB)

#### /data/observations/ - Verification and Analysis Data
```
aifs_single_winds.grib2                # AIFS-Single 10m wind components subset
aifs_single_winds.grib2.5b7b6.idx      # Index for AIFS-Single wind data
analysis_winds.grib2                    # Analysis/observation wind verification data
analysis_winds.grib2.5b7b6.idx         # Index for analysis wind data (variant 1)
analysis_winds.grib2.da267.idx         # Index for analysis wind data (variant 2)
data.grib2                              # Miscellaneous analysis data
ecmwf_ifs_data.grib2                   # Additional ECMWF IFS data (backup)
ifs_winds.grib2                         # IFS 10m wind components subset (9.0 MB)
ifs_winds.grib2.da267.idx              # Index for IFS wind data
```

#### /data/forecasts/ - Model Forecast Data
**aifs_single/** (Deterministic AI Integrated Forecasting System)
```
aifs_single_day1.grib2                 # Day 1 forecast
aifs_single_day1.grib2.5b7b6.idx       # Index for day 1
aifs_single_day2.grib2                 # Day 2 forecast
aifs_single_day2.grib2.5b7b6.idx       # Index for day 2
aifs_single_day3.grib2                 # Day 3 forecast
aifs_single_day3.grib2.5b7b6.idx       # Index for day 3
```

**ifs/** (Integrated Forecasting System - Baseline)
```
ifs_day1.grib2                          # Day 1 forecast
ifs_day1.grib2.5b7b6.idx               # Index variant 1 for day 1
ifs_day1.grib2.da267.idx                # Index variant 2 for day 1
ifs_day2.grib2                          # Day 2 forecast
ifs_day2.grib2.5b7b6.idx               # Index variant 1 for day 2
ifs_day2.grib2.da267.idx                # Index variant 2 for day 2
ifs_day3.grib2                          # Day 3 forecast
ifs_day3.grib2.5b7b6.idx               # Index variant 1 for day 3
ifs_day3.grib2.da267.idx                # Index variant 2 for day 3
```

#### /data/era5/ - ERA5 Reanalysis Initialization Data
```
era5_initial_state.nc                   # ERA5 initial state 3D atmospheric fields (81 MB)
era5_initial_surface.nc                 # ERA5 surface fields (8.0 MB)
```

#### /data/indices/ - GRIB Index Files
```
aifs_single_winds.grib2.5b7b6.idx      # Index for AIFS-Single wind data
analysis_winds.grib2.5b7b6.idx         # Index for analysis wind data
ifs_winds.grib2.5b7b6.idx              # Index for IFS wind data
```

#### /data/Met eireann/ - Hourly Weather Station Observations
**hourly-clare-shannonairport/**
```
Data_Licence.pdf                        # Data license
Data_Licence.txt                        # Data license text
KeyHourly.txt                           # Data keys and descriptions
hly518.csv                              # Shannon Airport hourly data
hourly-clare-shannonairport.zip         # Zipped version
```

**hourly-cork-corkairport/**
```
Data_Licence.pdf
Data_Licence.txt
KeyHourly.txt
hly3904.csv                             # Cork Airport hourly data
hourly-cork-corkairport.zip
```

**hourly-cork-sherkin/**
```
Data_Licence.pdf
Data_Licence.txt
KeyHourly.txt
hly775.csv                              # Sherkin Island hourly data
hourly-cork-sherkin.zip
```

**hourly-donegal-malinhead/**
```
Data_Licence.pdf
Data_Licence.txt
KeyHourly.txt
hly1575.csv                             # Malin Head hourly data
hourly-donegal-malinhead.zip
```

**hourly-dublin-pheonixpark/**
```
Data_Licence.pdf
Data_Licence.txt
KeyHourly.txt
hly175.csv                              # Dublin Phoenix Park hourly data
hourly-dublin-pheonixpark.zip
```

**hourly-kerry-valentia/**
```
Data_Licence.pdf
Data_Licence.txt
KeyHourly.txt
hly2275.csv                             # Valentia Island hourly data
hourly-kerry-valentia.zip
```

**houryl-galway-macehead/**
```
Data_Licence.pdf
Data_Licence.txt
KeyHourly.txt
hly275.csv                              # Mace Head (Galway) hourly data
houryl-galway-macehead.zip
```

#### /data/Bouy data/ - Offshore Buoy Data
```
bouy locations.png                      # Map visualization of buoy locations
bouy_details.txt                        # Details about buoy locations
buoy_long_lat.png                       # Buoy latitude/longitude visualization
m2.pdf                                  # M2 Buoy data
m3.pdf                                  # M3 Buoy data
m4.pdf                                  # M4 Buoy data
m5.pdf                                  # M5 Buoy data
m6.pdf                                  # M6 Buoy data
```

#### /data/ - Root Level CSV Files
```
dly3923.csv                             # Daily weather data
dly532.csv                              # Daily weather data
```

---

### /docs/ - Documentation and Configuration (28 KB)
```
ANALYSIS_GUIDE.md                       # Detailed analysis methodology and interpretation guide
README.md                               # Project overview
requirements.txt                        # Python package dependencies
pip_install.log                         # Package installation log
```

---

### /notebooks/ - Jupyter Analysis Notebooks (572 KB)

#### /notebooks/analysis/ - Primary Analysis Workflow
```
wind_analysis.ipynb                     # Complete 15-step analysis pipeline
                                        # STEP 1-3: Setup, configuration, initialization
                                        # STEP 4-7: Data loading and extraction
                                        # STEP 8-10: Statistical comparison and bias analysis
                                        # STEP 11-14: Comprehensive visualizations
                                        # STEP 15: Summary report generation

aifs_inference.ipynb                    # Revised roadmap for AIFS offshore/coastal extreme winds
                                        # Focus: AIFS skill for offshore/coastal extreme wind events
                                        # Includes methodology notes and implementation steps

analysis_winds.grib2                    # Analysis wind data (GRIB format)
era5_winds_2024_01.nc                   # ERA5 winds for January 2024 (NetCDF format)

create_new_notebook_demo.ipynb           # Demonstration notebook for programmatic notebook creation
```

#### /notebooks/exploratory/ - Exploratory Development
```
aifs1.ipynb                             # Initial methodology and exploration
aifs2.ipynb                             # Additional exploration and testing
```

#### /notebooks/reference/ - Reference Implementations
```
run_AIFS_v1.ipynb                       # AIFS model inference and testing reference
```

---

### /outputs/ - Generated Outputs and Results (164 KB)

#### /outputs/visualizations/ - Generated Visualizations
```
wind_comparison.png                     # Visualization of wind model comparison
```

---

## File Summary by Type

### Jupyter Notebooks (.ipynb)
- wind_analysis.ipynb - Main analysis pipeline
- aifs_inference.ipynb - AIFS-specific analysis
- create_new_notebook_demo.ipynb - Demo notebook
- aifs1.ipynb - Exploratory
- aifs2.ipynb - Exploratory
- run_AIFS_v1.ipynb - Reference

### GRIB2 Files (Weather Model Data)
- aifs_single_day*.grib2 (3 files) - AIFS deterministic forecasts
- ifs_day*.grib2 (3 files) - IFS forecasts
- aifs_single_winds.grib2 - AIFS wind subset
- ifs_winds.grib2 - IFS wind subset
- analysis_winds.grib2 - Analysis winds
- data.grib2 - Miscellaneous

### GRIB Index Files (.idx)
- Multiple .5b7b6.idx variants
- Multiple .da267.idx variants
- Used for fast access to GRIB data

### NetCDF Files (.nc)
- era5_initial_state.nc - ERA5 3D atmospheric state
- era5_initial_surface.nc - ERA5 surface fields
- era5_winds_2024_01.nc - ERA5 winds January 2024

### CSV Files (Tabular Data)
- hly*.csv - Hourly Met Éireann observations (7 stations)
- dly*.csv - Daily weather data (2 files)

### Documentation Files
- config.json - Configuration with station coordinates and parameters
- implementation_guide.md - Step-by-step tasks
- roadmap description.md - Project methodology
- DIRECTORY_STRUCTURE.md - Directory overview
- ANALYSIS_GUIDE.md - Detailed analysis methodology
- README.md - Project overview
- requirements.txt - Python dependencies

### Data Information Files
- KeyHourly.txt - Data column descriptions
- Data_Licence.txt/pdf - Data usage licenses
- bouy_details.txt - Buoy location information

### Visualization Files
- wind_comparison.png - Output visualization
- bouy locations.png - Buoy map
- buoy_long_lat.png - Buoy coordinates visualization

---

## Key Data Sources

### Forecast Models
- **AIFS-Single**: Deterministic AI forecasts (days 1-3)
- **IFS**: Integrated Forecasting System physics-based forecasts (days 1-3)
- **AIFS-Ensemble**: AI ensemble forecasts (referenced in config but data may be separate)

### Reference Data
- **ERA5**: Reanalysis data at initial state and surface
- **Met Éireann**: 7 hourly observation stations (onshore/coastal)
- **Buoys**: M2, M3, M4, M5, M6 offshore locations

### Locations Covered
**Onshore (4 stations):**
- Dublin (Phoenix Park)
- Shannon (Shannon Airport)
- Cork (Cork Airport)
- Galway (Mace Head)

**Coastal (3 stations):**
- Valentia (Valentia Observatory)
- Malin Head (Malin Head Weather Station)
- Sherkin Island (Sherkin Island Weather Station)

**Offshore (5 buoys):**
- M2, M3, M4, M5, M6

---

## Analysis Parameters (from config.json)

- **Duration**: 7 days
- **Lead times**: 24, 48, 72, 96, 120, 144 hours
- **Wind variables**: 10m (u, v), 100m (u, v), gusts
- **Offshore high wind threshold**: 20.0 m/s
- **Offshore fixed threshold**: 15.0 m/s
- **Percentile threshold**: 95th percentile
- **Time window**: 2024-01-01 to 2026-01-11
- **Grid resolution**: 0.25°

---

## Total Project Size
- **Data**: 337 MB
- **Notebooks**: 572 KB
- **Docs**: 28 KB
- **Outputs**: 164 KB
- **Total**: ~338 MB
