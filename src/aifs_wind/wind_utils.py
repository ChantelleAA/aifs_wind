"""
Wind Forecast Evaluation Utilities

This module contains utility functions for loading, processing, and analyzing
wind forecast data from AIFS, IFS, ERA5, and observational sources.

Author: Chantelle
Date: January 2026
"""

import numpy as np
import pandas as pd
import xarray as xr
from datetime import datetime, timedelta
from pathlib import Path
import warnings

# Suppress warnings
warnings.filterwarnings('ignore')


class DataLoader:
    """Class for loading various data sources."""
    
    @staticmethod
    def load_met_eireann_station(filepath):
        """
        Load Met Éireann hourly station data.
        
        Parameters:
        -----------
        filepath : str or Path
            Path to the CSV file
            
        Returns:
        --------
        df : pd.DataFrame
            DataFrame with datetime index and wind measurements
        """
        try:
            df = pd.read_csv(filepath)
            
            # Examine the first few rows to understand format
            print(f"Loading {filepath}")
            print(f"Columns: {df.columns.tolist()}")
            
            # Try to parse datetime - Met Éireann typically uses 'date' column
            date_cols = [col for col in df.columns if 'date' in col.lower()]
            if date_cols:
                df['datetime'] = pd.to_datetime(df[date_cols[0]], errors='coerce')
            
            # If there's also a time column, combine them
            time_cols = [col for col in df.columns if col.lower() in ['time', 'hour']]
            if time_cols and date_cols:
                df['datetime'] = pd.to_datetime(
                    df[date_cols[0]].astype(str) + ' ' + df[time_cols[0]].astype(str),
                    errors='coerce'
                )
            
            df.set_index('datetime', inplace=True)
            df = df.dropna(subset=[df.index.name])
            
            # Extract wind speed and direction
            # Common column names: wdsp, wind, ws, wind_speed, etc.
            wind_speed_cols = [col for col in df.columns 
                             if any(x in col.lower() for x in ['wdsp', 'wind', 'ws'])]
            
            if wind_speed_cols:
                # Take the first wind speed column
                df['wind_speed'] = pd.to_numeric(df[wind_speed_cols[0]], errors='coerce')
                
            # Wind direction
            wind_dir_cols = [col for col in df.columns 
                           if any(x in col.lower() for x in ['wddir', 'wd', 'wind_dir'])]
            if wind_dir_cols:
                df['wind_direction'] = pd.to_numeric(df[wind_dir_cols[0]], errors='coerce')
            
            print(f"Loaded {len(df)} records from {df.index.min()} to {df.index.max()}")
            
            return df
            
        except Exception as e:
            print(f"Error loading {filepath}: {e}")
            return None
    
    @staticmethod
    def load_era5_at_location(lat, lon, era5_file, variable='wind'):
        """
        Load ERA5 reanalysis at specific location.
        
        Parameters:
        -----------
        lat : float
            Latitude
        lon : float
            Longitude
        era5_file : str or Path
            Path to ERA5 NetCDF file
        variable : str
            'wind' for u10/v10 components or specific variable name
            
        Returns:
        --------
        data : dict
            Dictionary with time series data
        """
        try:
            ds = xr.open_dataset(era5_file)
            
            # ERA5 longitude is 0-360, may need conversion
            if lon < 0:
                lon_era5 = lon + 360
            else:
                lon_era5 = lon
            
            # Select nearest point
            point = ds.sel(latitude=lat, longitude=lon_era5, method='nearest')
            
            data = {
                'time': point['time'].values,
                'lat': float(point['latitude'].values),
                'lon': float(point['longitude'].values)
            }
            
            # Extract wind components if available
            if 'u10' in ds.variables:
                data['u10'] = point['u10'].values
            if 'v10' in ds.variables:
                data['v10'] = point['v10'].values
            
            # Compute wind speed if components available
            if 'u10' in data and 'v10' in data:
                data['wind_speed'] = np.sqrt(data['u10']**2 + data['v10']**2)
            
            return data
            
        except Exception as e:
            print(f"Error loading ERA5 at ({lat}, {lon}): {e}")
            return None
    
    @staticmethod
    def load_grib_at_location(lat, lon, grib_file, filter_keys=None):
        """
        Load GRIB2 forecast data at specific location.
        
        Parameters:
        -----------
        lat : float
            Latitude
        lon : float
            Longitude  
        grib_file : str or Path
            Path to GRIB2 file
        filter_keys : dict, optional
            Dictionary of keys to filter (e.g., {'typeOfLevel': 'heightAboveGround'})
            
        Returns:
        --------
        data : dict
            Dictionary with forecast time series
        """
        try:
            import cfgrib
            
            # Open GRIB file
            if filter_keys:
                ds = xr.open_dataset(grib_file, engine='cfgrib',
                                    backend_kwargs={'filter_by_keys': filter_keys})
            else:
                ds = xr.open_dataset(grib_file, engine='cfgrib')
            
            # Handle longitude convention
            if lon < 0 and ds.longitude.max() > 180:
                lon_grib = lon + 360
            else:
                lon_grib = lon
            
            # Select location
            point = ds.sel(latitude=lat, longitude=lon_grib, method='nearest')
            
            data = {
                'latitude': float(point['latitude'].values),
                'longitude': float(point['longitude'].values),
                'time': point['time'].values if 'time' in point else None,
                'valid_time': point['valid_time'].values if 'valid_time' in point else None,
                'step': point['step'].values if 'step' in point else None
            }
            
            # Extract wind components - handle different naming conventions
            # ECMWF uses '10u' and '10v' for 10m winds
            if 'u10' in ds.variables:
                data['u10'] = point['u10'].values
            elif '10u' in ds.variables:
                data['u10'] = point['10u'].values
            elif 'u' in ds.variables:
                data['u10'] = point['u'].values
                
            if 'v10' in ds.variables:
                data['v10'] = point['v10'].values
            elif '10v' in ds.variables:
                data['v10'] = point['10v'].values
            elif 'v' in ds.variables:
                data['v10'] = point['v'].values
                
            # Compute wind speed
            if 'u10' in data and 'v10' in data:
                data['wind_speed'] = np.sqrt(data['u10']**2 + data['v10']**2)
            
            # Close dataset
            ds.close()
            
            return data
            
        except Exception as e:
            print(f"Error loading GRIB at ({lat}, {lon}): {e}")
            import traceback
            traceback.print_exc()
            return None
    
    @staticmethod
    def load_forecast_from_new_structure(model_key, date_offset, init_time, lead_time, lat, lon):
        """
        Load forecast data from the new ecmwf_forecasts structure.
        
        Parameters:
        -----------
        model_key : str
            'ifs', 'aifs_single', or 'aifs_ensemble'
        date_offset : int
            Days from today (0=today, -1=yesterday, etc.)
        init_time : str
            Initialization time ('00z', '06z', '12z', '18z')
        lead_time : int
            Forecast lead time in hours
        lat, lon : float
            Location coordinates
            
        Returns:
        --------
        data : dict
            Wind data at location
        """
        from pathlib import Path
        
        # Get file path using config helper
        try:
            from config_updated import get_forecast_files
            files = get_forecast_files(model_key, date_offset, init_time, lead_time)
        except ImportError:
            # Fallback: construct path manually
            base = Path("ecmwf_forecasts")
            if model_key == 'ifs':
                path = base / "ifs" / "oper"
                ftype = 'fc'
            elif model_key == 'aifs_single':
                path = base / "aifs-single" / "oper"
                ftype = 'fc'
            elif model_key == 'aifs_ensemble':
                path = base / "aifs-ens" / "enfo"
                ftype = 'cf'  # Use control forecast
            else:
                return None
            
            date_dir = f"date{date_offset:+d}"
            type_dir = f"type-{ftype}"
            step_file = f"step-{lead_time:03d}h.grib2"
            files = path / date_dir / init_time / type_dir / step_file
        
        # Handle ensemble (list of files) vs deterministic (single file)
        if isinstance(files, list):
            # For ensemble, load control forecast
            file_to_load = files[0] if files else None
        else:
            file_to_load = files
        
        if file_to_load is None or not Path(file_to_load).exists():
            return None
        
        # Load the file at the specified location
        return DataLoader.load_grib_at_location(lat, lon, file_to_load)


class WindMetrics:
    """Class for computing wind-related metrics and statistics."""
    
    @staticmethod
    def compute_wind_speed(u, v):
        """Compute wind speed from u and v components."""
        return np.sqrt(u**2 + v**2)
    
    @staticmethod
    def compute_wind_direction(u, v):
        """
        Compute wind direction from u and v components.
        Returns direction in degrees (0-360) where 0° = North.
        """
        direction = np.arctan2(-u, -v) * 180 / np.pi
        direction = (direction + 360) % 360
        return direction
    
    @staticmethod
    def define_extreme_events(wind_speed, method='percentile', 
                             threshold=None, percentile=90):
        """
        Define extreme wind events.
        
        Parameters:
        -----------
        wind_speed : array-like
            Wind speed time series
        method : str
            'percentile', 'absolute', or 'both'
        threshold : float
            Absolute threshold in m/s
        percentile : float
            Percentile for extreme definition
            
        Returns:
        --------
        extreme_mask : boolean array
            True where extreme events occur
        threshold_value : float or tuple
            Threshold value(s) used
        """
        wind_speed = np.array(wind_speed)
        
        if method == 'percentile':
            threshold_value = np.nanpercentile(wind_speed, percentile)
            extreme_mask = wind_speed >= threshold_value
        
        elif method == 'absolute':
            if threshold is None:
                threshold_value = 17.2  # Beaufort 8 (gale)
            else:
                threshold_value = threshold
            extreme_mask = wind_speed >= threshold_value
        
        elif method == 'both':
            percentile_threshold = np.nanpercentile(wind_speed, percentile)
            absolute_threshold = threshold if threshold else 17.2
            extreme_mask = ((wind_speed >= percentile_threshold) | 
                          (wind_speed >= absolute_threshold))
            threshold_value = (percentile_threshold, absolute_threshold)
        
        return extreme_mask, threshold_value


class ForecastVerification:
    """Class for forecast verification metrics."""
    
    @staticmethod
    def calculate_basic_metrics(forecast, observed):
        """
        Calculate basic forecast verification metrics.
        
        Returns dictionary with bias, MAE, RMSE, correlation, etc.
        """
        # Remove NaN values
        valid_mask = ~(np.isnan(forecast) | np.isnan(observed))
        forecast = np.array(forecast)[valid_mask]
        observed = np.array(observed)[valid_mask]
        
        if len(forecast) == 0:
            return None
        
        # Basic metrics
        bias = np.mean(forecast - observed)
        mae = np.mean(np.abs(forecast - observed))
        rmse = np.sqrt(np.mean((forecast - observed)**2))
        correlation = np.corrcoef(forecast, observed)[0, 1] if len(forecast) > 1 else np.nan
        
        # R-squared
        ss_res = np.sum((observed - forecast)**2)
        ss_tot = np.sum((observed - np.mean(observed))**2)
        r_squared = 1 - (ss_res / ss_tot) if ss_tot != 0 else np.nan
        
        return {
            'n_samples': len(forecast),
            'bias': bias,
            'mae': mae,
            'rmse': rmse,
            'correlation': correlation,
            'r_squared': r_squared,
            'mean_forecast': np.mean(forecast),
            'mean_observed': np.mean(observed),
            'std_forecast': np.std(forecast),
            'std_observed': np.std(observed)
        }
    
    @staticmethod
    def calculate_categorical_metrics(forecast, observed, threshold):
        """
        Calculate categorical forecast metrics for extreme events.
        
        Returns POD, FAR, CSI, hits, misses, false alarms.
        """
        forecast_extreme = np.array(forecast) >= threshold
        observed_extreme = np.array(observed) >= threshold
        
        # Contingency table
        hits = np.sum(forecast_extreme & observed_extreme)
        misses = np.sum(~forecast_extreme & observed_extreme)
        false_alarms = np.sum(forecast_extreme & ~observed_extreme)
        correct_negatives = np.sum(~forecast_extreme & ~observed_extreme)
        
        # Skill scores
        pod = hits / (hits + misses) if (hits + misses) > 0 else np.nan
        far = false_alarms / (hits + false_alarms) if (hits + false_alarms) > 0 else np.nan
        csi = hits / (hits + misses + false_alarms) if (hits + misses + false_alarms) > 0 else np.nan
        
        return {
            'threshold': threshold,
            'hits': hits,
            'misses': misses,
            'false_alarms': false_alarms,
            'correct_negatives': correct_negatives,
            'pod': pod,  # Probability of Detection
            'far': far,  # False Alarm Ratio
            'csi': csi   # Critical Success Index
        }
    
    @staticmethod
    def calculate_ensemble_metrics(ensemble_members, observed, threshold=None):
        """
        Calculate ensemble-specific metrics.
        
        Parameters:
        -----------
        ensemble_members : array, shape (n_members, n_times)
            Ensemble forecast members
        observed : array, shape (n_times,)
            Observed values
        threshold : float, optional
            Threshold for probabilistic extreme event metrics
            
        Returns:
        --------
        metrics : dict
            Ensemble verification metrics
        """
        ensemble_members = np.array(ensemble_members)
        observed = np.array(observed)
        
        # Ensemble statistics
        ensemble_mean = np.mean(ensemble_members, axis=0)
        ensemble_spread = np.std(ensemble_members, axis=0)
        
        # CRPS (simplified)
        crps = np.mean([np.mean(np.abs(member - observed)) 
                       for member in ensemble_members])
        
        # Spread-error relationship
        forecast_error = np.abs(ensemble_mean - observed)
        spread_error_ratio = np.nanmean(ensemble_spread) / np.nanmean(forecast_error)
        
        metrics = {
            'n_members': ensemble_members.shape[0],
            'ensemble_mean': ensemble_mean,
            'ensemble_spread': ensemble_spread,
            'mean_spread': np.nanmean(ensemble_spread),
            'crps': crps,
            'spread_error_ratio': spread_error_ratio
        }
        
        # Probabilistic metrics for extremes
        if threshold is not None:
            exceedance_prob = np.mean(ensemble_members >= threshold, axis=0)
            observed_extreme = observed >= threshold
            
            # Brier Score
            brier_score = np.mean((exceedance_prob - observed_extreme.astype(float))**2)
            
            metrics.update({
                'exceedance_probability': exceedance_prob,
                'brier_score': brier_score
            })
        
        return metrics


# Beaufort scale thresholds
BEAUFORT_SCALE = {
    0: {'name': 'Calm', 'min': 0.0, 'max': 0.3},
    1: {'name': 'Light air', 'min': 0.3, 'max': 1.6},
    2: {'name': 'Light breeze', 'min': 1.6, 'max': 3.4},
    3: {'name': 'Gentle breeze', 'min': 3.4, 'max': 5.5},
    4: {'name': 'Moderate breeze', 'min': 5.5, 'max': 8.0},
    5: {'name': 'Fresh breeze', 'min': 8.0, 'max': 10.8},
    6: {'name': 'Strong breeze', 'min': 10.8, 'max': 13.9},
    7: {'name': 'Near gale', 'min': 13.9, 'max': 17.2},
    8: {'name': 'Gale', 'min': 17.2, 'max': 20.8},
    9: {'name': 'Strong gale', 'min': 20.8, 'max': 24.5},
    10: {'name': 'Storm', 'min': 24.5, 'max': 28.5},
    11: {'name': 'Violent storm', 'min': 28.5, 'max': 32.7},
    12: {'name': 'Hurricane', 'min': 32.7, 'max': np.inf}
}


def get_beaufort_scale(wind_speed):
    """Get Beaufort scale number for given wind speed (m/s)."""
    for scale, info in BEAUFORT_SCALE.items():
        if info['min'] <= wind_speed < info['max']:
            return scale
    return 12  # Hurricane force


if __name__ == "__main__":
    print("Wind Forecast Evaluation Utilities Module")
    print("Available classes:")
    print("  - DataLoader: Load ERA5, GRIB, and station data")
    print("  - WindMetrics: Compute wind speed, direction, extremes")
    print("  - ForecastVerification: Calculate verification metrics")