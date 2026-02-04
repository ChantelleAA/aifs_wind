#!/usr/bin/env python3
"""
Extract Marine Buoy Data from PDFs - FIXED VERSION
Parses the text directly since columns are: 
Col 0: Time
Col 3: Wind Dir (°)
Col 4: Wind Speed (kn)
Col 5: Max Gust (kn)
"""

import pandas as pd
import numpy as np
from pathlib import Path
import re
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

BUOYS = {
    'M2_Buoy': 'm2.pdf',
    'M3_Buoy': 'm3.pdf',
    'M4_Buoy': 'm4.pdf',
    'M5_Buoy': 'm5.pdf',
    'M6_Buoy': 'm6.pdf'
}

def extract_from_pdf_text(pdf_path):
    """Extract by reading PDF as text and parsing lines"""
    try:
        import pdfplumber
    except ImportError:
        import subprocess
        subprocess.check_call(['pip', 'install', 'pdfplumber', '--break-system-packages'])
        import pdfplumber
    
    all_rows = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            
            for line in text.split('\n'):
                # Skip header and non-data lines
                if not line or 'Sensor Name' in line or 'Time' in line or 'Please click' in line:
                    continue
                
                # Check if line starts with a date (format: DD/MM/YYYY HH:MM:SS)
                match = re.match(r'^(\d{2}/\d{2}/\d{4})\s+(\d{2}:\d{2}:\d{2})', line)
                if not match:
                    continue
                
                try:
                    # Extract datetime
                    date_part = match.group(1)
                    time_part = match.group(2)
                    datetime_str = f"{date_part} {time_part}"
                    
                    # Remove datetime from line to parse rest
                    rest = line[match.end():]
                    parts = rest.split()
                    
                    if len(parts) < 4:
                        continue
                    
                    # Parts now: [pressure, char, press_tend, wind_dir, wind_speed, gust, ...]
                    wind_dir = float(parts[2])      # Wind direction (degrees)
                    wind_speed_kt = float(parts[3]) # Wind speed (knots)
                    max_gust_kt = float(parts[4]) if len(parts) > 4 else np.nan
                    
                    # Convert knots to m/s
                    wind_speed_ms = wind_speed_kt * 0.514444
                    max_gust_ms = max_gust_kt * 0.514444 if not np.isnan(max_gust_kt) else np.nan
                    
                    all_rows.append({
                        'datetime': datetime_str,
                        'wind_dir_deg': wind_dir,
                        'wind_speed_kt': wind_speed_kt,
                        'wind_speed_ms': wind_speed_ms,
                        'max_gust_kt': max_gust_kt,
                        'max_gust_ms': max_gust_ms,
                        'air_temp_c': np.nan
                    })
                except (ValueError, IndexError) as e:
                    continue
    
    if not all_rows:
        return None
    
    df = pd.DataFrame(all_rows)
    df['datetime'] = pd.to_datetime(df['datetime'], format='%d/%m/%Y %H:%M:%S', errors='coerce')
    df = df.dropna(subset=['datetime'])
    df = df.sort_values('datetime')
    
    return df


def main():
    print("="*80)
    print("MARINE BUOY DATA EXTRACTION - FIXED VERSION")
    print("="*80)
    
    output_dir = Path(__file__).parent.parent / 'data' / 'Bouy data'
    
    for buoy_name, pdf_file in BUOYS.items():
        pdf_path = output_dir / pdf_file
        
        if not pdf_path.exists():
            print(f"\n✗ {buoy_name}: PDF not found ({pdf_path})")
            continue
        
        print(f"\n{buoy_name}:")
        print(f"  Extracting from: {pdf_path}")
        
        df = extract_from_pdf_text(pdf_path)
        
        if df is None or len(df) == 0:
            print(f"  ✗ No data extracted")
            continue
        
        # Save
        output_file = output_dir / f'{buoy_name.lower()}.csv'
        df.to_csv(output_file, index=False)
        
        # Stats
        print(f"  ✓ Extracted {len(df)} observations")
        print(f"  Date range: {df['datetime'].min()} to {df['datetime'].max()}")
        print(f"  Mean wind: {df['wind_speed_ms'].mean():.2f} m/s (range: {df['wind_speed_ms'].min():.2f}-{df['wind_speed_ms'].max():.2f})")
        print(f"  ✓ Saved: {output_file}")
    
    print("\n" + "="*80)
    print("✓ EXTRACTION COMPLETE")
    print("="*80)


if __name__ == '__main__':
    main()