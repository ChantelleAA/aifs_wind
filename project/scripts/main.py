#!/usr/bin/env python3
"""
Main orchestrator for ECMWF Open Data downloads.
Runs IFS, AIFS-Single, and AIFS-ENS downloads sequentially.
"""

import logging
import subprocess
import sys
from pathlib import Path
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

SCRIPTS_DIR = Path(__file__).parent

def run_script(script_name: str) -> bool:
    """Run a download script and return True if successful"""
    script_path = SCRIPTS_DIR / script_name
    logger.info(f"Starting {script_name}")
    
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            check=True,
            capture_output=False  # Let output flow to terminal
        )
        logger.info(f"✓ {script_name} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"✗ {script_name} failed with exit code {e.returncode}")
        return False
    except Exception as e:
        logger.error(f"✗ {script_name} failed: {e}")
        return False

def main():
    start_time = datetime.now()
    logger.info("="*80)
    logger.info("ECMWF Open Data Download - Starting")
    logger.info(f"Start time: {start_time}")
    logger.info("="*80)
    
    scripts = [
        "download_ifs.py",
        "download_aifs_single.py",
        "download_aifs_ens.py"
    ]
    
    results = {}
    for script in scripts:
        results[script] = run_script(script)
    
    end_time = datetime.now()
    duration = end_time - start_time
    
    logger.info("="*80)
    logger.info("ECMWF Open Data Download - Summary")
    logger.info(f"Duration: {duration}")
    for script, success in results.items():
        status = "SUCCESS" if success else "FAILED"
        logger.info(f"  {script}: {status}")
    logger.info("="*80)
    
    # Exit with error code if any script failed
    if not all(results.values()):
        sys.exit(1)

if __name__ == "__main__":
    main()