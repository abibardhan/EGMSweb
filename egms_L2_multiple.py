import os
import zipfile
from io import BytesIO
import curl_cffi.requests as curl_requests
from time import sleep

# Configuration
BASE_URL = "https://egms.land.copernicus.eu/insar-api/archive/download/EGMS_{data_type}_{relative_orbit}_{burst_cycle}_{swath}_{polarization}_{year}_1.zip?id={id}"
DOWNLOAD_BASE = "Point_downloads"
ID = "7ce01544f73b4a9780b56f9c96fe4de3"
YEAR = "2018_2022"  # 2018_2022, 2019_2023, 2020_2024
DATA_TYPE = "L2a"   # L2a or L2b

# Parameter ranges
RELATIVE_ORBIT_MIN = 50
RELATIVE_ORBIT_MAX = 52
BURST_CYCLE_MIN = 715
BURST_CYCLE_MAX = 717
SWATHS = ["IW1", "IW2", "IW3"]         # Available swaths
POLARIZATIONS = ["VV", "VH"]           # Available polarizations
DELAY = 5  # seconds between requests to avoid overwhelming the server

def download_tile(data_type, relative_orbit, burst_cycle, swath, polarization):
    """Download a single L2 tile with given parameters"""
    # Format with appropriate zero padding
    rel_orbit_str = f"{relative_orbit:03d}"  # 3-digit format (e.g., 052)
    burst_cycle_str = f"{burst_cycle:04d}"   # 4-digit format (e.g., 0716)
    
    filename_prefix = f"EGMS_{data_type}_{rel_orbit_str}_{burst_cycle_str}_{swath}_{polarization}_{YEAR}_1"
    url = BASE_URL.format(
        data_type=data_type,
        relative_orbit=rel_orbit_str, 
        burst_cycle=burst_cycle_str, 
        swath=swath, 
        polarization=polarization, 
        year=YEAR, 
        id=ID
    )
    
    try:
        response = curl_requests.get(url, timeout=600)  # 10 minutes timeout
        print(f"Response for {filename_prefix}: {response.status_code}")
        
        if response.status_code != 200:
            print(f"Failed to download {filename_prefix}")
            sleep(10)  # Extra delay after failure
            return False
        
        # Create download directory if it doesn't exist
        os.makedirs(DOWNLOAD_BASE, exist_ok=True)
        
        # Read zip from memory
        with zipfile.ZipFile(BytesIO(response.content)) as z:
            for name in z.namelist():
                if name.endswith(".csv") and filename_prefix in name:
                    z.extract(name, path=DOWNLOAD_BASE)
                    print(f"Extracted {name}")
                    return True
        
        print(f"No matching CSV found in the downloaded zip for {filename_prefix}")
        return False
    
    except Exception as e:
        print(f"Error downloading {filename_prefix}: {e}")
        return False

if __name__ == "__main__":
    print(f"=== EGMS L2 Batch Download Tool ===")
    print(f"Downloading {DATA_TYPE} data with the following parameters:")
    print(f"  Relative Orbits: {RELATIVE_ORBIT_MIN} to {RELATIVE_ORBIT_MAX}")
    print(f"  Burst Cycles: {BURST_CYCLE_MIN} to {BURST_CYCLE_MAX}")
    print(f"  Swaths: {', '.join(SWATHS)}")
    print(f"  Polarizations: {', '.join(POLARIZATIONS)}")
    print(f"  Year: {YEAR}")
    
    # Calculate total combinations
    orbit_count = RELATIVE_ORBIT_MAX - RELATIVE_ORBIT_MIN + 1
    burst_count = BURST_CYCLE_MAX - BURST_CYCLE_MIN + 1
    swath_count = len(SWATHS)
    pol_count = len(POLARIZATIONS)
    total_combinations = orbit_count * burst_count * swath_count * pol_count
    
    print(f"\nTotal combinations to try: {total_combinations}")
    print(f"Estimated time: ~{(total_combinations * DELAY) / 60:.1f} minutes")
    
    successful = 0
    failed = 0
    current_task = 0
    
    for rel_orbit in range(RELATIVE_ORBIT_MIN, RELATIVE_ORBIT_MAX + 1):
        for burst_cycle in range(BURST_CYCLE_MIN, BURST_CYCLE_MAX + 1):
            for swath in SWATHS:
                for polarization in POLARIZATIONS:
                    current_task += 1
                    rel_orbit_str = f"{rel_orbit:03d}"
                    burst_cycle_str = f"{burst_cycle:04d}"
                    
                    print(f"\n[{current_task}/{total_combinations}] Processing {DATA_TYPE}_{rel_orbit_str}_{burst_cycle_str}_{swath}_{polarization}...")
                    
                    success = download_tile(DATA_TYPE, rel_orbit, burst_cycle, swath, polarization)
                    
                    if success:
                        successful += 1
                        print(f"✓ Successfully downloaded {DATA_TYPE}_{rel_orbit_str}_{burst_cycle_str}_{swath}_{polarization}")
                    else:
                        failed += 1
                        print(f"✗ Failed to download {DATA_TYPE}_{rel_orbit_str}_{burst_cycle_str}_{swath}_{polarization}")
                    
                    # Add delay between requests (except for the last one)
                    if current_task < total_combinations:
                        print(f"Waiting {DELAY} seconds before next request...")
                        sleep(DELAY)
    
    print(f"\n=== Download Summary ===")
    print(f"Total combinations attempted: {total_combinations}")
    print(f"Successfully downloaded: {successful}")
    print(f"Failed: {failed}")
    print(f"Success rate: {(successful/total_combinations)*100:.1f}%") 