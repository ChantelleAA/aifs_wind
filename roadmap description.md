# Roadmap: Evaluating AIFS Skill for Offshore and Coastal Extreme Winds Around Ireland

## Experimentation Focus

**Primary focus:**
Evaluate the ability of the Artificial Intelligence Forecasting System (AIFS) to predict offshore and coastal extreme wind events around Ireland.

**Secondary focus:**
Compare forecast performance across offshore, coastal, and onshore environments, and assess whether AIFS ensemble forecasts provide earlier or more reliable indications of extreme wind events than deterministic forecasts.

---

## Core Research Questions

1. How accurately does AIFS predict high and extreme wind speeds in offshore environments?
2. Does AIFS systematically underestimate or fail to capture extreme wind events, particularly near the coast?
3. Is AIFS more reliable offshore than onshore, where surface roughness and terrain effects are significant?
4. Does the AIFS ensemble improve the detection and early warning of extreme wind events compared to AIFS-Single?
5. How does AIFS performance compare with the traditional physics-based IFS at the same locations?

---

## Overall Strategy

Rather than averaging wind fields over large spatial domains, this project adopts a point-based evaluation approach. The methodology consists of:

* Selecting representative onshore, coastal, and offshore locations
* Extracting wind time series at these fixed locations
* Comparing forecast outputs with ERA5 reanalysis and available observations
* Focusing explicitly on high and extreme wind conditions

Each location is treated independently, allowing local forecast behaviour to be assessed directly.

---

## Step 1: Define Vantage Points

### 1.1 Onshore Stations

**Purpose:**

* Provide ground-truth reference
* Assess forecast performance near land
* Evaluate land–sea transition effects

**Examples:**

* Dublin (east coast)
* Shannon (west)
* Cork
* Galway

**Data sources:**

* Met Éireann station observations
* ERA5 at station coordinates

---

### 1.2 Coastal Stations

**Purpose:**

* Assess forecast skill in high-impact coastal zones
* Capture wind behaviour during storm landfall
* Evaluate relevance for coastal hazard forecasting

**Examples:**

* Valentia Island
* Sherkin Island
* Additional west and southwest coastal sites

**Data sources:**

* Met Éireann station observations
* ERA5
* Forecast data sampled at the nearest grid point

---

### 1.3 Offshore Points

**Purpose:**

* Primary focus of the analysis
* Direct relevance to offshore wind and marine applications
* Reduced influence of surface roughness and terrain

**Options:**

* Existing offshore buoys, where data are available
* Fixed offshore grid points, following standard practice in forecast verification

**Placement:**

* Atlantic west of Ireland
* Celtic Sea
* Irish Sea for comparison

**Data sources:**

* ERA5 reanalysis as the primary reference
* AIFS and IFS forecast outputs

---

## Step 2: Data Collection

### 2.1 Forecast Data

* AIFS-Single (deterministic)
* AIFS-Ensemble (probabilistic)
* IFS (baseline physics-based model)

**Requirements:**

* Historical forecast runs
* 10 m wind components (u10, v10)
* Consistent forecast lead times

---

### 2.2 Reference Data

**ERA5 Reanalysis**

* Primary reference dataset, particularly offshore
* Spatially complete and physically consistent

**Met Éireann Observations**

* Used where available at onshore and coastal locations
* Independent reference for evaluating extreme wind behaviour

---

## Step 3: Time and Location Alignment

For each vantage point:

* Match forecast valid times with corresponding ERA5 and observation times
* Ensure consistency in:

  * UTC time
  * Measurement height (10 m)
  * Units

All analyses are conducted at fixed points; no spatial averaging is applied.

---

## Step 4: Wind Speed Computation

At each location and time step:

* Compute wind speed from vector components:

  * √(u² + v²)
* Construct time series for:

  * AIFS-Single
  * AIFS-Ensemble (all members)
  * IFS
  * ERA5
  * Observations, where available

---

## Step 5: Definition of Extreme Wind Events

Extreme wind events are defined locally for each location to reflect local climatology.

Possible definitions include:

* Wind speeds exceeding 15–20 m/s at offshore locations
* The upper 5% or 10% of wind speeds at each point
* Periods associated with known storm events

This approach avoids the use of arbitrary global thresholds.

---

## Step 6: Model Evaluation at Each Location

For each vantage point, compute standard deterministic performance metrics:

* Bias
* Root Mean Square Error (RMSE)
* Correlation
* Missed extreme events
* False alarms

Event-based analysis addresses:

* Whether extreme events were predicted
* Accuracy of event timing
* Accuracy of predicted wind magnitude

---

## Step 7: Ensemble-Based Extreme Wind Analysis

For the AIFS ensemble:

* Estimate the probability of exceeding extreme wind thresholds
* Analyse ensemble spread during high-wind events
* Assess forecast skill as a function of lead time

Key questions include:

* Whether ensemble forecasts provide earlier indications of risk
* Whether higher ensemble probabilities correspond to observed extremes
* Whether ensemble information is more informative offshore than onshore

---

## Step 8: Offshore, Coastal, and Onshore Comparison

Results are aggregated by environmental category:

* Offshore locations
* Coastal locations
* Onshore locations

Comparisons focus on:

* Bias and error characteristics
* Extreme event detection rates
* Added value of ensemble forecasts

This enables a direct assessment of how forecast performance varies across environments.

---

## Step 9: Interpretation and Application

Results are interpreted in the context of:

* Offshore wind energy applications
* Coastal hazard forecasting
* Operational use of AIFS ensemble products
