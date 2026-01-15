#!/usr/bin/env python3
"""
Download ECMWF open forecast data for the past N days using ecmwf-opendata.

Models covered (as per https://data.ecmwf.int/forecasts/):
  - ifs
  - aifs-single
  - aifs-ens

Notes:
  - Runs are at 00/06/12/18 UTC.
  - aifs-ens typically uses types: cf, pf (control / perturbed).
  - aifs-single + ifs deterministic commonly use type: fc.
"""

from __future__ import annotations

from pathlib import Path
from typing import Iterable

from ecmwf.opendata import Client


# ---- configure what you want to download ----
DAYS_BACK = 3  # past 3 days (today + previous 2)
RUN_TIMES = [0, 6, 12, 18]  # UTC cycles
STEPS = [0, 6, 12, 24]      # forecast lead times (hours) - change as you like

# A small, common starter set (2m temp, 10m winds, mslp).
# You can add/remove params; ECMWF param short names apply.
PARAMS = ["2t", "10u", "10v", "msl"]

# Which model+stream+type combos to fetch
JOBS = [
    # IFS deterministic atmosphere (oper stream)
    {"model": "ifs", "stream": "oper", "types": ["fc"]},

    # AIFS single (oper stream)
    {"model": "aifs-single", "stream": "oper", "types": ["fc"]},

    # AIFS ensemble (enfo stream): control + perturbed
    {"model": "aifs-ens", "stream": "enfo", "types": ["cf", "pf"]},
]


def safe_retrieve(client: Client, request: dict, target: Path) -> bool:
    """Return True if downloaded, False if missing/unavailable."""
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        client.retrieve(request=request, target=str(target))
        return True
    except Exception as e:
        # Common when a particular run/step/type isn't published yet.
        print(f"SKIP: {target.name} ({e.__class__.__name__}: {e})")
        return False


def iter_dates(days_back: int) -> Iterable[int]:
    """
    ecmwf-opendata supports date=0 (today), date=-1 (yesterday), etc.
    We'll yield 0, -1, -2, ...
    """
    for d in range(days_back):
        yield -d


def main(out_dir: str = "ecmwf_forecasts"):
    base = Path(out_dir)

    for job in JOBS:
        model = job["model"]
        stream = job["stream"]
        types = job["types"]

        client = Client(source="ecmwf", model=model)  # source can also be aws/google/azure

        for date in iter_dates(DAYS_BACK):
            for time in RUN_TIMES:
                for typ in types:
                    for step in STEPS:
                        # Build request. Keep it explicit.
                        request = {
                            "date": date,
                            "time": time,
                            "type": typ,
                            "step": step,
                            "stream": stream,
                            "param": PARAMS,
                        }

                        # Nice, structured filenames
                        # We don't know the resolved datetime until after retrieval,
                        # so we encode requested date offset + cycle time.
                        target = (
                            base
                            / model
                            / stream
                            / f"date{date:+d}"
                            / f"{time:02d}z"
                            / f"type-{typ}"
                            / f"step-{step:03d}h.grib2"
                        )

                        ok = safe_retrieve(client, request, target)
                        if ok:
                            print(f"OK:   {target}")

    print("Done.")


if __name__ == "__main__":
    main()
