import os
import zipfile
from io import BytesIO
import curl_cffi.requests as curl_requests

# Configuration
BASE_URL = "https://egms.land.copernicus.eu/insar-api/archive/download/EGMS_{data_type}_{relative_orbit}_{burst_cycle}_{swath}_{polarization}_{year}_1.zip?id={id}"
DOWNLOAD_BASE = "Point_downloads"
ID = "7ce01544f73b4a9780b56f9c96fe4de3"
YEAR = "2018_2022"  # 2018_2022, 2019_2023, 2020_2024
DATA_TYPE = "L2a"  # L2a or L2b
RELATIVE_ORBIT = "052"  # e.g., 052
BURST_CYCLE = "0716"    # e.g., 0716
SWATH = "IW2"           # IW1, IW2, IW3
POLARIZATION = "VV"     # VV, VH, HH, HV

def download_tile(data_type, relative_orbit, burst_cycle, swath, polarization):
    """Download a single L2 tile with given parameters"""
    filename_prefix = f"EGMS_{data_type}_{relative_orbit}_{burst_cycle}_{swath}_{polarization}_{YEAR}_1"
    url = BASE_URL.format(
        data_type=data_type,
        relative_orbit=relative_orbit, 
        burst_cycle=burst_cycle, 
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
    print(f"=== EGMS L2 Download Tool ===")
    print(f"Downloading {DATA_TYPE} data:")
    print(f"  Relative Orbit: {RELATIVE_ORBIT}")
    print(f"  Burst Cycle: {BURST_CYCLE}")
    print(f"  Swath: {SWATH}")
    print(f"  Polarization: {POLARIZATION}")
    print(f"  Year: {YEAR}")
    
    success = download_tile(DATA_TYPE, RELATIVE_ORBIT, BURST_CYCLE, SWATH, POLARIZATION)
    
    if success:
        print(f"Successfully downloaded {DATA_TYPE}_{RELATIVE_ORBIT}_{BURST_CYCLE}_{SWATH}_{POLARIZATION}")
    else:
        print(f"Failed to download {DATA_TYPE}_{RELATIVE_ORBIT}_{BURST_CYCLE}_{SWATH}_{POLARIZATION}") 