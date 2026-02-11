import json
from pathlib import Path
import logging
from utils import yyyymmdd_utc, parse_available_cycles, looks_complete
from ecmwf.opendata import Client

CONFIG_PATH = Path(__file__).parent.parent / 'config.json'
with open(CONFIG_PATH, "r") as f:
    config = json.load(f)

aifs_config = config["MODELS"]["aifs-ens"]
source = config.get("SOURCE", "ecmwf")
days_back = config.get("DAYS_BACK", 3)
init_times = config.get("INIT_TIMES", ["00z", "12z"])
out_dir = Path(config.get("OUT_DIR"))
base_url = config.get("BASE_URL", "https://data.ecmwf.int")

LEAD_TIMES = list(range(0, 144, 3)) + list(range(144, 241, 6))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def target_path(date_str: str, init_time: str, typ: str, step_h: int,
                stream: str, levtype: str, level: int = None) -> Path:
    full_path = (Path(out_dir) / "aifs-ens" / f"{stream}" / f"date{date_str}" /
                 f"{init_time}" / f"type-{typ}" / f"levtype-{levtype}" /
                 f"step-{step_h:03d}h.grib2")
    if level is not None:
        full_path = full_path.with_name(full_path.stem + f"-lev{level}hPa" + full_path.suffix)
    return full_path

def download_one(client: Client, date_str: str, init_time: str, typ: str,
                 step_h: int, stream: str, params: list[str], levtype: str,
                 levelist: list[int] = None, level: int = None) -> None:
    output_path = target_path(date_str, init_time, typ, step_h, stream, levtype, level)
    
    if looks_complete(output_path):
        logger.info(f"SKIP (exists): {output_path}")
        return
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    request = {
        "date": date_str,
        "time": int(init_time[:-1]),
        "step": step_h,
        "type": typ,
        "stream": stream,
        "levtype": levtype,
        "param": params,
    }
    
    if levtype == "pl":
        request["levelist"] = levelist
    
    logger.info(f"GET: {date_str} {init_time} {stream}/{typ} step={step_h:03d}h {levtype} -> {output_path.name}")
    
    try:
        client.retrieve(request, str(output_path))
        logger.info(f"SUCCESS: {output_path.name}")
    except Exception as e:
        logger.error(f"FAILED: {output_path.name} -> {e}")
        if output_path.exists() and output_path.stat().st_size < 50_000:
            try:
                output_path.unlink()
            except Exception:
                pass

def main():
    logger.info("="*80)
    logger.info("Starting AIFS-ENS download")
    logger.info(f"Output directory: {out_dir}")
    logger.info("="*80)
    
    client = Client(source=source, model="aifs-ens")
    
    for days_ago in range(days_back):
        date_str = yyyymmdd_utc(days_ago)
        
        try:
            available_cycles = parse_available_cycles(date_str, base_url + "/forecasts")
        except Exception as e:
            logger.warning(f"Could not check cycles for {date_str}: {e}")
            continue
        
        wanted_cycles = [c for c in init_times if c in available_cycles]
        
        if not wanted_cycles:
            logger.info(f"{date_str}: No matching cycles")
            continue
        
        logger.info(f"{date_str}: Processing cycles {wanted_cycles}")
        
        for init_time in wanted_cycles:
            for product in aifs_config["products"]:
                stream = product["stream"]
                product_type = product["type"]
                surface_params = product["surface_params"]
                
                for step_h in LEAD_TIMES:
                    download_one(
                        client=client,
                        date_str=date_str,
                        init_time=init_time,
                        typ=product_type,
                        step_h=step_h,
                        stream=stream,
                        params=surface_params,
                        levtype="sfc"
                    )
                    
                    download_one(
                        client=client,
                        date_str=date_str,
                        init_time=init_time,
                        typ=product_type,
                        step_h=step_h,
                        stream=stream,
                        params=aifs_config["pressure_level_params"],
                        levtype="pl",
                        levelist=aifs_config["pressure_levels"]
                    )
    
    logger.info("="*80)
    logger.info("AIFS-ENS download complete")
    logger.info("="*80)

if __name__ == "__main__":
    main()