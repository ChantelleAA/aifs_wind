"""
AIFS Wind Forecast Evaluation Package

Core modules for wind forecast evaluation and analysis.
"""

__version__ = "1.0.0"
__author__ = "Chantelle"
__date__ = "February 2026"

from .wind_utils import DataLoader, WindMetrics, ForecastVerification
from .config import LOCATIONS, MODEL_CONFIGS, LEAD_TIMES, INIT_TIMES

__all__ = [
    'DataLoader',
    'WindMetrics',
    'ForecastVerification',
    'LOCATIONS',
    'MODEL_CONFIGS',
    'LEAD_TIMES',
    'INIT_TIMES'
]
