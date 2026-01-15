import pandas as pd
import matplotlib.pyplot as plt
import sys

# Try to read from multiple possible locations
possible_paths = [
    'wind_speed_timeseries.csv',
    '../wind_speed_timeseries.csv',
    '../../wind_speed_timeseries.csv'
]

df = None
for path in possible_paths:
    try:
        df = pd.read_csv(path)
        print(f"✓ Loaded data from: {path}")
        break
    except:
        continue

if df is None:
    print("ERROR: Could not find wind_speed_timeseries.csv")
    print("Please run this script from your aifs_wind directory")
    sys.exit(1)

# Filter to only locations with observations
df_with_obs = df[df['Observed'].notna()].copy()

print(f"\nLocations with observations: {len(df_with_obs['Location'].unique())}")
print(f"Locations: {', '.join(sorted(df_with_obs['Location'].unique()))}")

# ============================================================================
# PLOT 1: ALL LOCATIONS SUBPLOT GRID
# ============================================================================
fig, axes = plt.subplots(3, 4, figsize=(20, 12))
fig.suptitle('Wind Speed Forecasts vs Observations - All Locations', 
             fontsize=20, fontweight='bold', y=0.995)

locations = sorted(df_with_obs['Location'].unique())

for idx, location in enumerate(locations):
    if idx >= 12:
        break
    
    row = idx // 4
    col = idx % 4
    ax = axes[row, col]
    
    loc_data = df_with_obs[df_with_obs['Location'] == location].copy()
    loc_data = loc_data.sort_values('Lead_Time_h')
    
    env = loc_data['Environment'].iloc[0]
    env_colors = {
        'onshore': '#27AE60',
        'coastal': '#F39C12', 
        'offshore': '#16A085'
    }
    
    lead_times = loc_data['Lead_Time_h'].values
    
    # Observations (black dots)
    ax.scatter(lead_times, loc_data['Observed'], 
              s=150, color='black', marker='o', 
              label='Observed', zorder=5, edgecolors='white', linewidths=1.5)
    
    # IFS (red)
    ax.plot(lead_times, loc_data['IFS'], 
           marker='s', markersize=8, linewidth=2, 
           color='#E74C3C', label='IFS', alpha=0.8)
    
    # AIFS Single (teal)
    ax.plot(lead_times, loc_data['AIFS_Single'], 
           marker='^', markersize=8, linewidth=2,
           color='#16A085', label='AIFS Single', alpha=0.8)
    
    # AIFS Ensemble (navy)
    ax.plot(lead_times, loc_data['AIFS_Ens_Mean'], 
           marker='D', markersize=7, linewidth=2,
           color='#2C3E50', label='AIFS Ensemble', alpha=0.8)
    
    # Ensemble spread (shaded)
    if (loc_data['AIFS_Ens_Std'] > 0).any():
        ax.fill_between(lead_times,
                        loc_data['AIFS_Ens_Mean'] - loc_data['AIFS_Ens_Std'],
                        loc_data['AIFS_Ens_Mean'] + loc_data['AIFS_Ens_Std'],
                        alpha=0.2, color='#2C3E50')
    
    ax.set_title(f"{location.replace('_', ' ')}\n({env})", 
                fontweight='bold', fontsize=11, 
                color=env_colors.get(env, 'black'))
    ax.set_xlabel('Lead Time (hours)', fontsize=9)
    ax.set_ylabel('Wind Speed (m/s)', fontsize=9)
    ax.grid(True, alpha=0.3, linestyle='--')
    ax.set_xticks([6, 12, 24])
    
    if idx == 0:
        ax.legend(loc='upper left', fontsize=8, framealpha=0.9)
    
    # Set y-limits
    all_vals = pd.concat([
        loc_data['Observed'],
        loc_data['IFS'],
        loc_data['AIFS_Single'],
        loc_data['AIFS_Ens_Mean']
    ]).dropna()
    
    if len(all_vals) > 0:
        y_min = max(0, all_vals.min() - 2)
        y_max = all_vals.max() + 2
        ax.set_ylim(y_min, y_max)

# Remove empty subplots
for idx in range(len(locations), 12):
    row = idx // 4
    col = idx % 4
    fig.delaxes(axes[row, col])

plt.tight_layout()
plt.savefig('forecast_vs_obs_all_locations.png', dpi=300, bbox_inches='tight')
print("\n✓ Saved: forecast_vs_obs_all_locations.png")

# ============================================================================
# PLOT 2: KEY EXAMPLES (1 ONSHORE, 1 COASTAL, 1 OFFSHORE)
# ============================================================================
representatives = {
    'onshore': 'Shannon_Airport',
    'coastal': 'Malin_Head',
    'offshore': 'M2_Buoy'
}

fig, axes = plt.subplots(1, 3, figsize=(18, 6))
fig.suptitle('Wind Speed Forecasts vs Observations - Key Examples', 
             fontsize=18, fontweight='bold')

env_colors = {
    'onshore': '#27AE60',
    'coastal': '#F39C12',
    'offshore': '#16A085'
}

for idx, (env, location) in enumerate(representatives.items()):
    ax = axes[idx]
    
    loc_data = df_with_obs[df_with_obs['Location'] == location].copy()
    
    if len(loc_data) == 0:
        print(f"WARNING: No data for {location}")
        continue
        
    loc_data = loc_data.sort_values('Lead_Time_h')
    lead_times = loc_data['Lead_Time_h'].values
    
    # Observations (large black dots)
    ax.scatter(lead_times, loc_data['Observed'], 
              s=200, color='black', marker='o', 
              label='Observed', zorder=5, edgecolors='white', linewidths=2)
    
    # IFS
    ax.plot(lead_times, loc_data['IFS'], 
           marker='s', markersize=10, linewidth=2.5, 
           color='#E74C3C', label='IFS', alpha=0.9)
    
    # AIFS Single
    ax.plot(lead_times, loc_data['AIFS_Single'], 
           marker='^', markersize=10, linewidth=2.5,
           color='#16A085', label='AIFS Single', alpha=0.9)
    
    # AIFS Ensemble
    ax.plot(lead_times, loc_data['AIFS_Ens_Mean'], 
           marker='D', markersize=9, linewidth=2.5,
           color='#2C3E50', label='AIFS Ensemble', alpha=0.9)
    
    # Ensemble spread
    if (loc_data['AIFS_Ens_Std'] > 0).any():
        ax.fill_between(lead_times,
                        loc_data['AIFS_Ens_Mean'] - loc_data['AIFS_Ens_Std'],
                        loc_data['AIFS_Ens_Mean'] + loc_data['AIFS_Ens_Std'],
                        alpha=0.25, color='#2C3E50')
    
    # Calculate statistics
    obs_mean = loc_data['Observed'].mean()
    ifs_bias = (loc_data['IFS'] - loc_data['Observed']).mean()
    aifs_bias = (loc_data['AIFS_Single'] - loc_data['Observed']).mean()
    ens_bias = (loc_data['AIFS_Ens_Mean'] - loc_data['Observed']).mean()
    
    ifs_rmse = ((loc_data['IFS'] - loc_data['Observed'])**2).mean()**0.5
    aifs_rmse = ((loc_data['AIFS_Single'] - loc_data['Observed'])**2).mean()**0.5
    ens_rmse = ((loc_data['AIFS_Ens_Mean'] - loc_data['Observed'])**2).mean()**0.5
    
    ax.set_title(f"{location.replace('_', ' ')}\n{env.upper()}", 
                fontweight='bold', fontsize=14,
                color=env_colors[env])
    
    # Statistics box
    stats_text = f"Obs Mean: {obs_mean:.2f} m/s\n"
    stats_text += f"\nBias:\n"
    stats_text += f"  IFS: {ifs_bias:+.2f} m/s\n"
    stats_text += f"  AIFS: {aifs_bias:+.2f} m/s\n"
    stats_text += f"  Ens: {ens_bias:+.2f} m/s\n"
    stats_text += f"\nRMSE:\n"
    stats_text += f"  IFS: {ifs_rmse:.2f} m/s\n"
    stats_text += f"  AIFS: {aifs_rmse:.2f} m/s\n"
    stats_text += f"  Ens: {ens_rmse:.2f} m/s"
    
    ax.text(0.02, 0.98, stats_text,
           transform=ax.transAxes,
           fontsize=9,
           verticalalignment='top',
           family='monospace',
           bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.85))
    
    ax.set_xlabel('Lead Time (hours)', fontsize=12, fontweight='bold')
    if idx == 0:
        ax.set_ylabel('Wind Speed (m/s)', fontsize=12, fontweight='bold')
    
    ax.grid(True, alpha=0.3, linestyle='--', linewidth=1)
    ax.set_xticks([6, 12, 24])
    ax.legend(loc='lower right', fontsize=10, framealpha=0.95)
    
    # Set y-limits
    all_vals = pd.concat([
        loc_data['Observed'],
        loc_data['IFS'],
        loc_data['AIFS_Single'],
        loc_data['AIFS_Ens_Mean']
    ]).dropna()
    
    if len(all_vals) > 0:
        y_min = max(0, all_vals.min() - 2)
        y_max = all_vals.max() + 3
        ax.set_ylim(y_min, y_max)

plt.tight_layout()
plt.savefig('forecast_vs_obs_key_examples.png', dpi=300, bbox_inches='tight')
print("✓ Saved: forecast_vs_obs_key_examples.png")

print("\n" + "="*80)
print("✓ ALL PLOTS CREATED SUCCESSFULLY")
print("="*80)
print("\n📊 Generated Files:")
print("  1. forecast_vs_obs_all_locations.png")
print("     → 3x4 grid showing all 11 locations with observations")
print("     → Black dots = observed, lines = models")
print("     → Ensemble spread shown as gray shading")
print("\n  2. forecast_vs_obs_key_examples.png")
print("     → Focused view of 3 representative locations:")
print("       • Shannon Airport (Onshore)")
print("       • Malin Head (Coastal)")  
print("       • M2 Buoy (Offshore)")
print("     → Statistics box shows bias & RMSE for each model")
print("     → Perfect for presentation discussion!")
print("="*80)