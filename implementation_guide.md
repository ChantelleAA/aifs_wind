# IMPLEMENTATION GUIDE: OFFSHORE & COASTAL EXTREME WIND ANALYSIS

*(AIFS vs IFS, validated with ERA5 and observations)*

---

## Overview

This guide outlines a **point-based analysis framework** to evaluate how well **AIFS** predicts **offshore and coastal extreme wind events** around Ireland.

Instead of spatial averaging, the analysis focuses on **specific onshore, coastal, and offshore locations** (vantage points) and compares forecast wind speeds against **ERA5 reanalysis** and **available observations**.

The emphasis is on:

* extreme wind events
* offshore performance
* added value of **AIFS ensemble forecasts**

---

## PROJECT OBJECTIVES

* Assess AIFS skill in predicting **high and extreme winds offshore**
* Compare AIFS performance **offshore vs coastal vs onshore**
* Evaluate whether **AIFS ensemble forecasts** improve extreme wind detection
* Benchmark AIFS against **IFS**
* Use ERA5 as a consistent reference, supplemented by station data where available

---

## TASK 1: Define Analysis Vantage Points

### Objective

Select fixed locations that represent **onshore**, **coastal**, and **offshore** wind regimes around Ireland.

### Implementation Steps

#### Step 1a: Onshore Stations

Purpose:

* Ground truth
* Land–sea transition reference

Examples:

* Dublin
* Shannon
* Cork
* Galway

Data sources:

* Met Éireann station observations
* ERA5 at station coordinates
* Forecasts sampled at nearest grid point

---

#### Step 1b: Coastal Stations

Purpose:

* High-impact storm zones
* Rapid wind changes near coastline

Examples:

* Valentia Island
* Sherkin Island
* West / southwest coastal sites

Data sources:

* Met Éireann observations
* ERA5
* Forecasts at nearest grid point

---

#### Step 1c: Offshore Points (Primary Focus)

Purpose:

* Offshore wind and marine relevance
* Cleaner wind physics

Options:

* Existing offshore buoys (if available)
* Fixed offshore grid points (standard approach)

Placement:

* Atlantic west of Ireland
* Celtic Sea
* Irish Sea (comparison region)

Data sources:

* ERA5 (primary reference)
* Forecasts at exact grid locations

---

## TASK 2: Collect Forecast and Reference Data

### Objective

Gather consistent historical datasets for comparison.

### Data Required

#### Forecasts

* AIFS-Single (deterministic)
* AIFS-Ensemble (all members)
* IFS (baseline)

Variables:

* 10 m wind components (u10, v10)

---

#### Reference Data

* ERA5 reanalysis (primary reference, especially offshore)
* Met Éireann station data (onshore & coastal where available)

---

## TASK 3: Align Time and Location

### Objective

Ensure all datasets are directly comparable.

### Implementation Steps

For each vantage point:

* Extract wind at **exact coordinates**
* Match **forecast valid times** with:

  * ERA5 timestamps
  * Observation timestamps (if available)
* Ensure:

  * UTC time
  * 10 m height
  * consistent units

**No spatial averaging** is applied.

---

## TASK 4: Compute Wind Speed Time Series

### Objective

Create comparable wind speed time series at each location.

### Implementation Steps

For each dataset:

* Compute wind speed:
  `wind = sqrt(u10² + v10²)`
* Build time series for:

  * AIFS-Single
  * AIFS-Ensemble (per member)
  * IFS
  * ERA5
  * Observations (if available)

---

## TASK 5: Define Extreme Wind Events

### Objective

Identify high-impact wind conditions in a consistent way.

### Possible Definitions

* Wind speed > **15–20 m/s** (offshore)
* Top **5–10%** of wind speeds at each point
* Known storm periods (optional)

Extremes are defined **locally per point**, not globally.

---

## TASK 6: Evaluate Deterministic Forecast Skill

### Objective

Quantify forecast accuracy at each vantage point.

### Metrics

* Bias
* RMSE
* Correlation
* Missed extreme events
* False alarms

### Analysis

Performed separately for:

* Offshore points
* Coastal points
* Onshore points

---

## TASK 7: Ensemble-Based Extreme Wind Analysis

### Objective

Assess whether AIFS ensemble forecasts improve extreme wind prediction.

### Implementation Steps

* Compute probability of exceeding extreme thresholds
* Calculate ensemble spread during high-wind periods
* Compare:

  * AIFS-Single vs AIFS-Ensemble
  * Detection rate of extreme events
  * Lead-time dependence

Key questions:

* Does the ensemble flag risk earlier?
* Is ensemble information more reliable offshore?

---

## TASK 8: Offshore vs Coastal vs Onshore Comparison

### Objective

Understand how forecast skill varies by environment.

### Analysis

Aggregate results by category:

* Offshore
* Coastal
* Onshore

Compare:

* Bias patterns
* Extreme detection rates
* Ensemble usefulness

---

## TASK 9: Reporting and Interpretation

### Objective

Summarize findings in a practical, decision-focused way.

### Outputs

* Point-based comparison tables
* Extreme event summaries
* Offshore vs coastal performance comparison
* Simple plots (time series, exceedance probabilities)

Optional:

* Storm case studies
* Offshore wind energy relevance

---

## IMPLEMENTATION CHECKLIST

* [ ] Define vantage points (onshore, coastal, offshore)
* [ ] Download historical forecasts
* [ ] Download ERA5 and station data
* [ ] Align time and location
* [ ] Compute wind speed
* [ ] Identify extreme events
* [ ] Evaluate deterministic forecasts
* [ ] Evaluate ensemble performance
* [ ] Compare offshore vs coastal vs onshore
* [ ] Summarize results

---

## One-Line Project Summary

> This project evaluates how well AIFS predicts offshore and coastal extreme wind events around Ireland by comparing historical forecasts against ERA5 and real observations at carefully selected onshore, coastal, and offshore locations.
