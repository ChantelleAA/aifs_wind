import json
from pathlib import Path
import logging
from utils import yyyymmdd_utc, parse_available_cycles, looks_complete
import os
from ecmwf.opendata import Client

CONFIG_PATH = Path(__file__).parent.parent / 'config.json'
with open(CONFIG_PATH, "r") as f:
    config = json.load(f)
    
ifs_config = config["MODELS"]["ifs"]

source = config.get("SOURCE", "ecmwf")
days_back = config.get("DAYS_BACK", 3)
init_times = config.get("INIT_TIMES", ["00z", "12z"])
out_dir = Path(config.get("OUT_DIR", str(Path(__file__).parent.parent / 'data' / 'ecmwf_forecasts')))
base_url = config.get("BASE_URL", "https://data.ecmwf.int")
resolution = config.get("RESOLUTION", "0p25")

# Generate full step range: 0-141 by 3, then 144-240 by 6
LEAD_TIMES = list(range(0, 144, 3)) + list(range(144, 241, 6))

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def target_path(date_str: str, init_time: str, typ: str, step_h: int, 
                stream: str, levtype: str, level: int = None) -> Path:
    """Build unique path for each IFS file"""
    full_path = (Path(out_dir) / "ifs" / f"{stream}" / f"date{date_str}" / 
                 f"{init_time}" / f"type-{typ}" / f"levtype-{levtype}" / 
                 f"step-{step_h:03d}h.grib2")
    if level is not None:
        full_path = full_path.with_name(full_path.stem + f"-lev{level}hPa" + full_path.suffix)
    return full_path

def download_one(client: Client, date_str: str, init_time: str, typ: str, 
                 step_h: int, stream: str, params: list[str], levtype: str, 
                 levelist: list[int] = None, level: int = None) -> None:
    """Download a single IFS file (surface or pressure level)"""
    
    output_path = target_path(date_str, init_time, typ, step_h, stream, levtype, level)
    
    if looks_complete(output_path):
        logger.info(f"SKIP (exists): {output_path}")
        return
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Build request
    request = {
        "date": date_str,
        "time": int(init_time[:-1]),  # "00z" -> 0
        "step": step_h,
        "type": typ,
        "stream": stream,
        "levtype": levtype,
        "param": params,
    }
    
    # Only add levelist for pressure level requests
    if levtype == "pl":
        request["levelist"] = levelist
    
    logger.info(f"GET: {date_str} {init_time} {stream}/{typ} step={step_h:03d}h {levtype} -> {output_path.name}")
    
    try:
        client.retrieve(request, str(output_path))
        logger.info(f"SUCCESS: {output_path.name}")
    except Exception as e:
        logger.error(f"FAILED: {output_path.name} -> {e}")
        # Clean up partial files
        if output_path.exists() and output_path.stat().st_size < 50_000:
            try:
                output_path.unlink()
                logger.info(f"Deleted partial file: {output_path.name}")
            except Exception:
                pass

def main():
    """Main loop: dates -> cycles -> products -> steps -> surface/pressure level"""
    
    logger.info("="*80)
    logger.info("Starting IFS download")
    logger.info(f"Output directory: {out_dir}")
    logger.info(f"Days back: {days_back}")
    logger.info(f"Init times: {init_times}")
    logger.info(f"Steps: {len(LEAD_TIMES)} steps from 0 to 240h")
    logger.info(f"Products: {len(ifs_config['products'])} (oper/fc, enfo/cf, enfo/pf)")
    logger.info("="*80)
    
    # Create client once
    client = Client(source=source, model="ifs")
    
    # Loop over dates
    for days_ago in range(days_back):
        date_str = yyyymmdd_utc(days_ago)
        
        # Check which cycles are available on the server
        try:
            available_cycles = parse_available_cycles(date_str, base_url + "/forecasts")
        except Exception as e:
            logger.warning(f"Could not check cycles for {date_str}: {e}")
            continue
        
        # Filter to only cycles we want AND that are available
        wanted_cycles = [c for c in init_times if c in available_cycles]
        
        if not wanted_cycles:
            logger.info(f"{date_str}: No matching cycles. Available={sorted(available_cycles)}, Wanted={init_times}")
            continue
        
        logger.info(f"{date_str}: Processing cycles {wanted_cycles}")
        
        # Loop over valid init times
        for init_time in wanted_cycles:
            
            # Loop over products (oper/fc, enfo/cf, enfo/pf)
            for product in ifs_config["products"]:
                stream = product["stream"]
                product_type = product["type"]
                surface_params = product["surface_params"]
                
                # Loop over steps
                for step_h in LEAD_TIMES:
                    
                    # Download surface params
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
                    
                    # Download pressure level params (all levels in one file)
                    download_one(
                        client=client,
                        date_str=date_str,
                        init_time=init_time,
                        typ=product_type,
                        step_h=step_h,
                        stream=stream,
                        params=ifs_config["pressure_level_params"],
                        levtype="pl",
                        levelist=ifs_config["pressure_levels"]
                    )
    
    logger.info("="*80)
    logger.info("IFS download complete")
    logger.info("="*80)

if __name__ == "__main__":
    main()