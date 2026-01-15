#!/usr/bin/env python3
"""
Download AIFS-ENS (ECMWF Open Data) in the exact folder structure expected by config.py/get_forecast_files.

Key features:
- AIFS-ENS only (stream=enfo, types=cf/pf)
- Uses INIT_TIMES and LEAD_TIMES from config.py if present
- FIRST checks what cycles are actually published on https://data.ecmwf.int/forecasts/
  and only downloads those (prevents pointless 404s)
- Skips files that already exist (and look complete)

Usage:
  python download_aifs_ens.py

Optional env vars:
  DAYS_BACK=3
  OUT_DIR=ecmwf_forecasts
  SOURCE=ecmwf   # or aws/azure/google (ecmwf-opendata supports these)
"""

from __future__ import annotations

import os
import re
from datetime import datetime, timedelta, timezone
from pathlib import Path

import requests
from ecmwf.opendata import Client


# ----------------------------
# Try to import your config.py
# ----------------------------
def load_project_config():
    try:
        import config as cfg  # type: ignore
        init_times = getattr(cfg, "INIT_TIMES", ["00z", "06z", "12z", "18z"])
        lead_times = getattr(cfg, "LEAD_TIMES", [6, 12, 24])
        return init_times, lead_times
    except Exception:
        return ["00z", "06z", "12z", "18z"], [6, 12, 24]


INIT_TIMES, LEAD_TIMES = load_project_config()

DAYS_BACK = int(os.environ.get("DAYS_BACK", "3"))
OUT_DIR = Path(os.environ.get("OUT_DIR", "ecmwf_forecasts"))
SOURCE = os.environ.get("SOURCE", "ecmwf")

MODEL = "aifs-ens"
STREAM = "enfo"
TYPES = ["cf", "pf"]
PARAMS = ["10u", "10v"]  # what you asked for


BASE = "https://data.ecmwf.int/forecasts"


def yyyymmdd_utc(days_ago: int) -> str:
    d = datetime.now(timezone.utc).date() - timedelta(days=days_ago)
    return d.strftime("%Y%m%d")


def parse_available_cycles(date_str: str) -> set[str]:
    """
    Query the ECMWF open-data directory listing for a specific date and return
    which init cycles exist (e.g., {'00z','06z'}).

    This prevents requesting non-existent 12z/18z and getting 404s.
    """
    url = f"{BASE}/{date_str}/"
    r = requests.get(url, timeout=30)
    r.raise_for_status()
    # Directory listings contain e.g. '00z/' '06z/' ...
    found = set(re.findall(r'>(\d{2})z/</a>', r.text))
    return {f"{hh}z" for hh in found}


def looks_complete(path: Path, min_bytes: int = 50_000) -> bool:
    """
    Very small GRIBs are usually failed/partial downloads.
    Adjust min_bytes if you want stricter checks.
    """
    return path.exists() and path.is_file() and path.stat().st_size >= min_bytes


def target_path(date_str: str, init_time: str, typ: str, step_h: int) -> Path:
    """
    Match your get_forecast_files() structure exactly:
      ecmwf_forecasts/aifs-ens/enfo/dateYYYYMMDD/00z/type-cf/step-006h.grib2
    """
    return (
        OUT_DIR
        / MODEL
        / STREAM
        / f"date{date_str}"
        / init_time
        / f"type-{typ}"
        / f"step-{step_h:03d}h.grib2"
    )


def download_one(client: Client, date_str: str, init_time: str, typ: str, step_h: int) -> None:
    t = target_path(date_str, init_time, typ, step_h)
    if looks_complete(t):
        print(f"SKIP (exists): {t}")
        return

    t.parent.mkdir(parents=True, exist_ok=True)

    hour = int(init_time[:2])  # "00z" -> 0, "06z" -> 6, etc.

    # IMPORTANT: use absolute date string so you download exactly what you want
    request = {
        "date": date_str,   # e.g. "20260111"
        "time": hour,       # 0, 6, 12, 18
        "stream": STREAM,   # "enfo"
        "type": typ,        # "cf" or "pf"
        "step": step_h,     # lead time in hours
        "param": PARAMS,    # 10u, 10v
    }

    print(f"GET: {date_str} {init_time} step={step_h:03d}h type={typ} -> {t}")
    try:
        client.retrieve(request=request, target=str(t))
    except Exception as e:
        # If it fails, remove any partial file to avoid poisoning future runs
        if t.exists() and t.stat().st_size < 50_000:
            try:
                t.unlink()
            except Exception:
                pass
        print(f"FAILED: {t} -> {e.__class__.__name__}: {e}")


def main():
    print("To ensure the stability of our systems and to preserve resources for our operational activities (network, compute, etc.), access to the open-data portal is limited to 500 simultaneous connections. This limit helps us guarantee reliable service for our operational users, especially during periods of high demand. For added reliability, the open-data is replicated across AWS, Azure, and Google Cloud. If you experience difficulties accessing the portal directly, you can also retrieve the data from these cloud platforms.")
    print(f"Downloading {MODEL} into: {OUT_DIR.resolve()}")
    print(f"DAYS_BACK:    {DAYS_BACK}")
    print(f"INIT_TIMES:   {INIT_TIMES}")
    print(f"LEAD_TIMES:   {LEAD_TIMES}")
    print(f"TYPES:        {TYPES}")
    print(f"PARAMS:       {PARAMS}")
    print("-" * 80)

    client = Client(source=SOURCE, model=MODEL)

    for days_ago in range(DAYS_BACK):
        date_str = yyyymmdd_utc(days_ago)

        try:
            available = parse_available_cycles(date_str)
        except Exception as e:
            print(f"WARNING: Could not read listing for {date_str} ({e.__class__.__name__}: {e})")
            continue

        # Only attempt cycles that are BOTH in your INIT_TIMES and published on the portal
        wanted = [t for t in INIT_TIMES if t in available]

        if not wanted:
            print(f"{date_str}: no published cycles matching INIT_TIMES={INIT_TIMES}. Published: {sorted(available)}")
            continue

        print(f"{date_str}: published cycles = {sorted(available)} | downloading cycles = {wanted}")

        for init_time in wanted:
            for step_h in LEAD_TIMES:
                for typ in TYPES:
                    download_one(client, date_str, init_time, typ, step_h)

    print("Done.")


if __name__ == "__main__":
    main()
