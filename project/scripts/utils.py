from datetime import datetime, timedelta, timezone
import json
import requests
import re
from pathlib import Path

   

def yyyymmdd_utc(days_ago: int) -> str:
    d = datetime.now(timezone.utc).date() - timedelta(days=days_ago)
    return d.strftime("%Y%m%d")

def parse_available_cycles(date_str: str, base_url) -> set[str]:
    """
    Query the ECMWF open-data directory listing for a specific date and return
    which init cycles exist (e.g., {'00z','06z'}).

    This prevents requesting non-existent 12z/18z and getting 404s.
    """
    url = f"{base_url}/{date_str}/"
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
