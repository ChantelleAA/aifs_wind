**First — an important clarification about what Open Data actually is**

Before anything else, you need to understand what you're actually working with here, because it has a direct bearing on your PhD.

Open Data is a **real-time, rolling dataset**. ECMWF runs its models four times a day and makes a subset of each run publicly available. But it only keeps the **most recent 12 forecast runs**, which amounts to roughly 2-3 days worth of data. After that, it's gone from Open Data forever.

This means Open Data is not a source of historical data — it never was. What it is, is a **live feed** that you can tap into daily to gradually accumulate your own historical dataset over time. That's exactly what your script was doing, or was supposed to be doing. The problem was your script was overwriting rather than appending, so you were only ever keeping the most recent run rather than building an archive.

This distinction matters enormously:
- **Open Data** = how you collect data going forward, day by day, building your own archive
- **MARS** = how you get data that already exists historically, going back years

Both are necessary for your project. MARS gives you the historical training data you need right now. Open Data is what keeps your dataset current as your PhD progresses.

---

**Understanding an ECMWF forecast run**

Before touching the API, you need to deeply understand what a forecast run actually is, because everything in the library maps onto this.

ECMWF runs its model four times every day, at **00z, 06z, 12z, and 18z** (z means UTC). Each run takes the current state of the atmosphere as its starting point — this starting point is called the **analysis** — and then projects forward in time, producing forecast fields at regular intervals called **steps**.

So when you make a request, you are always asking: *from which run (date + time), at which step forward in time, for which variables?*

For example: "give me the 10 metre wind from the run that started on 1st January 2025 at 00z, at step 24" means you want the model's prediction of 10 metre wind 24 hours after that run started, i.e. valid for 1st January 2025 at 00z + 24 hours = 2nd January 2025 at 00z.

This distinction between **run time** (when the model started) and **valid time** (what time the forecast is actually describing) is fundamental. Always keep both in mind.

---

**The model parameter — which forecasting system**

The client takes a `model` argument. Your three options are:

- `ifs` — the physics-based model, ECMWF's operational workhorse. This is what has been running for decades and is the foundation of almost all weather forecasting research. Default.
- `aifs-single` — the deterministic AI model, a single best-guess forecast
- `aifs-ens` — the ensemble AI model, 50 members representing forecast uncertainty

You'll be making separate requests for each model. They share the same parameter names but they are produced by entirely different systems, which is exactly why comparing them is scientifically interesting.

---

**The stream parameter — which product line within a model**

This is where it gets more nuanced. Within IFS, ECMWF runs several distinct product lines, and `stream` tells the library which one you want.

- `oper` — the high-resolution single deterministic forecast (HRES), run at 00z and 12z only
- `scda` — also HRES, but the 06z and 18z runs (lower priority, shorter range)
- `enfo` — the ensemble atmospheric forecast (ENS), 50 perturbed members plus a control
- `wave` — ocean wave fields from HRES
- `waef` — ocean wave fields from ENS

Since you've decided on 00z and 12z only, you'll primarily be using `oper` for the deterministic IFS, and `enfo` for the ensemble. The library can usually infer stream automatically if you leave `infer_stream_keyword=True`, which is the default — but understanding what it's doing under the hood matters.

For AIFS models, stream is also `enfo` for the ensemble, but the model parameter differentiates it from IFS ENS.

---

**The type parameter — what kind of forecast product**

Within a stream, there are different types of output:

- `fc` — a standard forecast. This is what you want for HRES/deterministic products.
- `pf` — perturbed forecast. These are the 50 individual ensemble members (each slightly different initial conditions)
- `cf` — control forecast. This is the one ensemble member run without perturbation, closest to the deterministic run
- `em` — ensemble mean. The average across all 50 members, a smoothed best estimate
- `es` — ensemble standard deviation. A measure of forecast spread/uncertainty at each grid point

For your research, the most important are `fc` for deterministic work, `pf` for working with individual ensemble members, and `em`/`es` for uncertainty quantification work.

---

**Parameters — what you're actually requesting physically**

Parameters are identified by short name strings. Here's what your key parameters actually mean physically, which matters for your research:

**Surface wind:**
- `10u` and `10v` — the wind at 10 metres above the surface, split into its west-east component (u) and south-north component (v). Wind is a vector, so you always need both components to know the full wind. To get wind speed you'd compute the square root of u² + v² yourself. To get direction you'd use arctan(u/v).
- `100u` and `100v` — same but at 100 metres, which is roughly hub height for modern offshore turbines. This is the most directly relevant parameter for turbine power output.
- `10fg` — the maximum wind gust in the period since the last forecast step. This is not an instantaneous value but a maximum over the interval. For extreme value analysis this is critical — the gust is often what causes structural damage, not the mean wind.

**Atmospheric context:**
- `msl` — mean sea level pressure. This tells you the synoptic-scale weather pattern. Low pressure systems drive the strongest wind events around Ireland.
- `sp` — surface pressure, which differs from msl because it's not corrected for elevation. Less useful for offshore work but relevant for air density calculations.
- `2t` — air temperature at 2 metres. Relevant because air density depends on temperature, and air density directly affects the power in the wind (power = ½ρAv³).

**Waves:**
- `swh` — significant wave height, the average of the highest third of waves. This is the standard metric for ocean state and directly relevant to offshore structural loading and access windows.
- `mwd` — the direction waves are coming from. Important because wave direction relative to turbine foundation orientation affects loading.
- `mwp` — the average wave period. Combined with height this determines wave energy and the dynamic loading frequency on structures.

**Pressure level parameters** — these describe the atmosphere at different heights above the surface. Each pressure level corresponds to a physical altitude:
- 1000 hPa ≈ near surface (about 100m)
- 925 hPa ≈ 750m
- 850 hPa ≈ 1500m
- 700 hPa ≈ 3000m
- 500 hPa ≈ 5500m
- 250 hPa ≈ 10500m (jet stream level)

At these levels you're requesting:
- `u` and `v` — wind components, same concept as surface but at altitude. The 850 hPa level is particularly important for forecasting surface wind because low-level jet streams and synoptic patterns are well-captured there.
- `gh` — geopotential height. This is how high a given pressure surface is above sea level. It's the fundamental variable for describing atmospheric circulation patterns and is what meteorologists use to draw weather maps.
- `t` — temperature at pressure levels, important for atmospheric stability calculations
- `q` — specific humidity, the mass of water vapour per unit mass of air. Affects buoyancy, stability, and indirectly wind behaviour through atmospheric dynamics.

---

**Steps — forecast lead times**

Steps are in hours. When you request `step=24` you get the forecast valid 24 hours after the run start time. You can request multiple steps at once as a list.

For your work you've settled on two distinct needs:
- Step 0 only — this is the analysis, the model's best estimate of the current state. No forecast skill involved, just model analysis.
- Steps out to 240 — the medium-range forecast out to day 10, which is the operationally relevant horizon for wind energy.

The step increment is 3-hourly from 0 to 144, then 6-hourly from 144 to 240 for HRES at 00z/12z. So the full list to day 10 is: 0, 3, 6, 9, ... 144, 150, 156, ... 240.

---

**How to think about structuring a request**

Every request you make answers these questions in order:

1. Which model? (`model`)
2. Which run date and time? (`date`, `time`)
3. Which product type within that model? (`stream`, `type`)
4. At which forecast lead time? (`step`)
5. Which variables? (`param`)
6. At which vertical levels, if pressure level data? (`levtype`, `levelist`)
7. Where do I save it? (`target`)

The library is deliberately designed around this logic. Work through these seven questions for any request you want to make and you'll always construct it correctly.

---

**The most important practical thing to understand**

Because Open Data only keeps the last 12 runs, your collection script needs to run **at least once every 2-3 days** to avoid gaps. Ideally it runs every day. Given you've already lost data due to the overwriting bug, the moment you fix that script you need to be disciplined about running it consistently.

The way to avoid overwriting is simple in concept — your target filename must be **unique per run**, incorporating the date and time in the filename. For example `ifs_hres_20250210_00z_step024.grib2` rather than `data.grib2`. That way each download goes to a new file and nothing is ever overwritten.
