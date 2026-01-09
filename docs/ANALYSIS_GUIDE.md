# Wind Model Comparison Analysis - Detailed Guide

## Overview
This guide helps you analyze whether ECMWF wind models (IFS, AIFS-Single, AIFS-Ensemble) underestimate wind speeds compared to actual observations, and identify trends in high wind events.

---

## PHASE 1: DATA ACQUISITION

### What Data You Need
1. **IFS Forecasts** - Traditional Integrated Forecasting System
   - Source: ECMWF Open Data
   - Frequency: 4 runs/day (00, 06, 12, 18 UTC)
   - Duration: Up to 10-day forecasts

2. **AIFS-Single** - AI-Based Deterministic Forecasts
   - Source: ECMWF Open Data
   - Frequency: 4 runs/day
   - Duration: Up to 15-day forecasts

3. **AIFS-Ensemble** - AI-Based Ensemble Predictions (optional)
   - Source: ECMWF Open Data
   - Frequency: 2 runs/day (00, 12 UTC)
   - Duration: Up to 10-day forecasts

4. **Analysis Data** - Observations/Reanalysis
   - Use IFS analysis fields (step 0)
   - Or ERA5 reanalysis data
   - Treated as "truth" for comparison

### Key Parameters to Download
- **10u, 10v**: 10-meter wind components (surface winds)
- **100u, 100v**: 100-meter wind components (wind energy relevant)
- **u, v**: Pressure level wind components
- **10fg**: 10-meter wind gusts (optional, for extreme analysis)

### Download Configuration
- **Resolution**: 0.25° (default and recommended)
- **Forecast steps**: 24h, 48h, 72h, 96h, 120h, 144h (1-6 days)
- **Time range**: Last 7 days minimum for statistically robust results

---

## PHASE 2: DATA LOADING & PREPROCESSING

### Load GRIB2 Files
```python
ds = xr.open_dataset(filename, engine="cfgrib")
```

### Calculate Wind Speed Magnitude
From U and V components:
$$\text{Wind Speed} = \sqrt{u^2 + v^2}$$

### Prepare Data for Comparison
- Calculate global mean wind speed for each forecast
- Organize by lead time (24h, 48h, etc.)
- Organize by forecast date

---

## PHASE 3: STATISTICAL COMPARISON

### Key Metrics to Calculate

#### 1. **Bias** (Most Important)
$$\text{Bias} = \overline{\text{Forecast} - \text{Analysis}}$$

- **Negative bias**: Model underestimates
- **Positive bias**: Model overestimates
- **Unit**: m/s and percentage

**Interpretation:**
- Bias > -5%: Acceptable
- Bias < -10%: Significant underestimation (problematic)

#### 2. **Percentage Bias**
$$\text{Bias\%} = \frac{\text{Bias}}{\text{Analysis Mean}} \times 100$$

**Critical for wind energy:**
- 10% underestimation → 19% power reduction (P ∝ V³)
- 20% underestimation → 49% power reduction

#### 3. **Mean Absolute Error (MAE)**
$$\text{MAE} = \overline{|\text{Forecast} - \text{Analysis}|}$$

Measures average magnitude of errors (lower is better).

#### 4. **Root Mean Square Error (RMSE)**
$$\text{RMSE} = \sqrt{\overline{(\text{Forecast} - \text{Analysis})^2}}$$

Penalizes large errors more heavily than MAE.

#### 5. **Correlation**
Measures how well model captures wind patterns (0-1 scale).

---

## PHASE 4: BIAS DETECTION - IS THE MODEL UNDERESTIMATING?

### Direct Assessment
```
If Bias < 0: Model UNDERESTIMATES
If Bias > 0: Model OVERESTIMATES
If |Bias| < 1 m/s: Model is UNBIASED
```

### Severity Scale
| Bias (%) | Bias (m/s) | Assessment | Wind Energy Impact |
|----------|-----------|------------|-------------------|
| < -20 | < -2.0 | CRITICAL underestimate | ✗ Dangerous |
| -20 to -10 | -2.0 to -1.0 | Significant underestimate | ⚠ Problematic |
| -10 to -2 | -1.0 to -0.2 | Slight underestimate | ≈ Minor bias |
| -2 to +2 | -0.2 to +0.2 | Unbiased / Accurate | ✓ Good |
| +2 to +10 | +0.2 to +1.0 | Slight overestimate | ≈ Minor bias |
| +10 to +20 | +1.0 to +2.0 | Significant overestimate | ⚠ Overconfident |
| > +20 | > +2.0 | CRITICAL overestimate | ✗ Unreliable |

---

## PHASE 5: LEAD TIME ANALYSIS

### What to Look For
1. **Does bias increase with lead time?**
   - Positive trend = Skill degradation
   - Flat = Stable performance

2. **Which model maintains accuracy longest?**
   - Critical for forecast applications

### Typical Patterns
- IFS often slightly underestimates
- AIFS models may have different bias profiles
- Bias often increases at 5-6 day lead times

---

## PHASE 6: HIGH WIND ANALYSIS

### Definition of "High Winds"
- **Threshold**: ≥ 12.5 m/s (typical wind warning threshold)
- Alternative: ≥ 10.8 m/s (Beaufort scale "high wind")
- **Gusts**: ≥ 15 m/s for strong gust warnings

### Analysis Steps
1. **Identify** forecasts with wind speeds > threshold
2. **Count** frequency of high wind events
3. **Compare bias** specifically during high wind events
4. **Determine** if model underestimates extreme speeds

### Critical Finding
**If model underestimates during high winds:**
- Safety implications (wind hazard warnings)
- Wind energy implications (turbine safety)
- Potential correction factor needed

---

## PHASE 7: TREND IDENTIFICATION

### Time-Based Trends
1. **Daily pattern**: Do certain days have higher winds?
2. **Forecast age**: Which forecasts are highest?
3. **Synoptic pattern**: Link to weather systems

### Model-Based Trends
1. **Which model performs best in high winds?**
2. **Do rankings change with lead time?**
3. **Is bias consistent across all conditions?**

### Event-Based Trends
1. **Top 10 windiest forecasts**: When do they occur?
2. **Model agreement**: Do all models agree on high wind events?
3. **Forecast confidence**: Higher agreement = more reliable

---

## INTERPRETATION GUIDE

### Scenario 1: Model Underestimates (-10% bias)
```
⚠ FINDING: All models underestimate by ~10%
IMPLICATION: 
  - Wind power underestimated by ~30%
  - Safety margins may be inadequate
  - Requires correction factor: multiply forecasts by 1.10

ACTION:
  - Inform stakeholders of systematic bias
  - Apply correction in operational use
  - Monitor bias separately for high wind events
```

### Scenario 2: AIFS Better Than IFS
```
✓ FINDING: AIFS-Single has 5% bias vs IFS 8% bias
IMPLICATION:
  - AI models capturing wind variations better
  - Potential value of new forecast products
  - Should consider transitioning to AIFS

ACTION:
  - Recommend AIFS-Single for operational use
  - Investigate why AIFS performs better
  - Plan transition strategy
```

### Scenario 3: Model Underestimates High Winds
```
⚠ CRITICAL FINDING: During high wind events, model bias increases to -15%
IMPLICATION:
  - Dangerous underestimation of wind hazards
  - Wind power during storms significantly underestimated
  - Safety risk for extreme weather operations

ACTION:
  - Apply larger correction factors for high wind forecasts
  - Issue additional quality flags for high wind events
  - Investigate physical causes (boundary layer, convection, etc.)
```

---

## VISUALIZATION INTERPRETATION

### Plot 1: Wind Speed by Lead Time
- **Interpretation**: Do all models converge? Are there model discontinuities?
- **High winds**: Look for spikes that indicate high wind periods
- **Trend**: Should generally remain relatively stable or slight decrease

### Plot 2: Bias Evolution
- **Flat line**: Stable performance across all lead times
- **Downward trend**: Degrading skill with lead time
- **Crossing zero**: Transition from over to underestimate

### Plot 3: Error Distribution
- **Skewed negative**: Systematic underestimation
- **Symmetric**: Random errors, unbiased
- **Leptokurtic (sharp peak)**: Consistent bias
- **Platykurtic (flat)**: Variable, unreliable

### Plot 4: Model Rankings
- **Clear winner**: Use that model operationally
- **Similar performance**: Consider ensemble of models
- **Poor rankings**: May need corrections before use

---

## PRACTICAL RECOMMENDATIONS

### For Wind Energy Applications
1. **Calculate bias-corrected forecasts**
   - Multiply by (1 + |bias|/100)
   - Monitor correction effectiveness over time

2. **Use ensemble approach**
   - Average multiple model predictions
   - Reduces individual model bias

3. **Focus on high wind skill**
   - Ensure accuracy when it matters most
   - Special attention to high wind bias

### For Research
1. **Document findings comprehensively**
   - Bias, RMSE, correlation for each model
   - Results by lead time and wind speed category

2. **Investigate causes**
   - Why do models underestimate?
   - Boundary layer parameterization issues?
   - Insufficient wind shear representation?

3. **Propose improvements**
   - Bias correction methods
   - Data assimilation enhancements
   - Model physics adjustments

### For Forecasters
1. **Monitor ongoing performance**
   - Re-evaluate bias monthly
   - Track if models improve or degrade

2. **Adjust uncertainty ranges**
   - Increase confidence intervals based on actual RMSE
   - Use observed bias to shade forecast ranges

3. **Quality flags**
   - Mark high wind forecasts for extra verification
   - Flag periods with unusual model disagreement

---

## CHECKLIST FOR COMPLETE ANALYSIS

- [ ] Downloaded 7+ days of forecast data from all 3 models
- [ ] Downloaded corresponding analysis/observation data
- [ ] Calculated global mean wind speeds for each forecast
- [ ] Calculated bias and RMSE metrics for each model
- [ ] Identified systematic underestimation (if any)
- [ ] Analyzed bias variation with forecast lead time
- [ ] Analyzed high wind event performance
- [ ] Created comprehensive visualizations
- [ ] Generated summary statistics table
- [ ] Identified top 10 windiest forecasts
- [ ] Written conclusions about model performance
- [ ] Made recommendations for operational use
- [ ] Documented any surprising findings

---

## COMMON QUESTIONS

**Q: Why does the model underestimate wind speeds?**
A: Common causes include:
- Insufficient horizontal resolution
- Boundary layer parameterization issues
- Inadequate wind shear representation
- Over-smoothing of wind fields

**Q: Should I always correct for bias?**
A: Yes, if bias is > ±5% and consistent. Apply: `forecast_corrected = forecast × (1 + bias)`

**Q: What's more important: bias or RMSE?**
A: For operational use, both matter:
- **Bias**: Systematic error (can be corrected)
- **RMSE**: Random error + uncertainty (harder to improve)

**Q: Can I use the ensemble mean?**
A: Yes, ensemble averaging typically reduces bias. Good for important forecasts.

**Q: How long should I analyze?**
A: Minimum 7 days for statistical robustness. 30 days or more for robust conclusions.

---

## References & Resources

- ECMWF Open Data: https://www.ecmwf.int/en/forecasts/datasets/open-data
- AIFS Model Documentation: https://www.ecmwf.int/en/research/projects/aifs
- xarray Documentation: https://docs.xarray.dev/
- Wind Energy Meteorology: IEA Wind Task 32

---

**Last Updated**: January 2026
**For Questions**: Refer to your notebook implementation for step-by-step code
