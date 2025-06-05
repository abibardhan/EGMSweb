import os
import csv
from tqdm import tqdm
from geopy.geocoders import Nominatim
import pyproj
from time import sleep

# Configuration
NAMES_DATASETS_DIR = "Point_locations"

# L2 dataset CSV path - update this to your downloaded L2 file
INPUT_CSV_PATH = "Point_downloads/EGMS_L2a_052_0716_IW2_VV_2018_2022_1.csv"

def init_transformer():
    """Initialize coordinate transformer from ETRS89/LAEA Europe to WGS84"""
    try:
        # EPSG:3035 is ETRS89-extended / LAEA Europe (commonly used for EGMS data)
        # EPSG:4326 is WGS84 (standard latitude/longitude)
        return pyproj.Transformer.from_crs("EPSG:3035", "EPSG:4326", always_xy=True)
    except Exception as e:
        print(f"Warning: Could not initialize coordinate transformer: {e}")
        return None

def convert_coordinates(easting, northing, transformer=None):
    """Convert easting/northing coordinates to latitude/longitude"""
    if transformer is None:
        # Fallback to initialize transformer if not provided
        transformer = init_transformer()
        if transformer is None:
            return None, None
    
    try:
        # Transform from projected coordinates to lat/lon
        lon, lat = transformer.transform(float(easting), float(northing))
        return lat, lon
    except Exception as e:
        print(f"Error converting coordinates: {e}")
        return None, None

def get_location_name(latitude, longitude):
    """Get location name for the given coordinates"""
    if latitude is None or longitude is None:
        return "Unknown location"
        
    geolocator = Nominatim(user_agent="egms-l2-cli")
    try:
        location = geolocator.reverse((latitude, longitude), exactly_one=True)
        if location:
            address = location.raw.get('address', {})
            city = address.get('city', address.get('town', address.get('village', '')))
            country = address.get('country', '')
            if city and country:
                return f"{city}, {country}"
            return location.address
        return "Unknown location"
    except Exception as e:
        print(f"Error in geocoding: {e}")
        return "Geocoding error"

def enrich_csv_with_locations(input_file):
    """Add location names to each point in the L2 CSV file"""
    if not os.path.exists(input_file):
        print(f"File not found: {input_file}")
        return
    
    # Create the names datasets directory if it doesn't exist
    os.makedirs(NAMES_DATASETS_DIR, exist_ok=True)
    
    # Get the base filename without path and extension
    base_filename = os.path.splitext(os.path.basename(input_file))[0]
    output_file = os.path.join(NAMES_DATASETS_DIR, f"{base_filename}_locations.csv")
    
    # Initialize coordinate transformer
    transformer = init_transformer()
    if transformer is None:
        print("Warning: Using approximate coordinate conversion")
    
    try:
        with open(input_file, 'r') as infile, open(output_file, 'w', newline='') as outfile:
            reader = csv.reader(infile)
            writer = csv.writer(outfile)
            
            # Read header
            header = next(reader)
            
            # Process headers (normalize to lowercase for case-insensitive matching)
            header_lower = [col.lower() for col in header]
            
            # Find column indices - L2 data might have different column names
            # Common possibilities: easting/northing, x/y, lon/lat
            easting_idx = None
            northing_idx = None
            
            # Try different column name variations
            for i, col in enumerate(header_lower):
                if col in ['easting', 'x', 'longitude', 'lon']:
                    easting_idx = i
                elif col in ['northing', 'y', 'latitude', 'lat']:
                    northing_idx = i
            
            if easting_idx is None or northing_idx is None:
                print(f"Required coordinate columns not found. Available columns: {header}")
                print("Looking for columns like: easting/northing, x/y, or longitude/latitude")
                return
                
            print(f"Found columns: easting/x={header[easting_idx]}, northing/y={header[northing_idx]}")
            
            # Create new header with location added after northing
            new_header = header.copy()
            new_header.insert(northing_idx + 1, 'location')
            
            # Write the new header
            writer.writerow(new_header)
            
            # Process each row
            for row in tqdm(reader, desc="Processing L2 coordinates"):
                easting = row[easting_idx]
                northing = row[northing_idx]
                
                # Convert from easting/northing to lat/lon
                lat, lon = convert_coordinates(easting, northing, transformer)
                
                # Get location name using converted coordinates
                location = get_location_name(lat, lon)
                sleep(0.5)  # 0.5s delay between requests to avoid overwhelming the service
                
                # Copy original row and insert location after northing
                new_row = row.copy()
                new_row.insert(northing_idx + 1, location)
                
                # Write the updated row
                writer.writerow(new_row)
                
        print(f"L2 location dataset saved as: {output_file}")
    
    except Exception as e:
        print(f"Error processing L2 CSV: {e}")
        import traceback
        traceback.print_exc()

def find_l2_files():
    """Find all L2 CSV files in the download directory"""
    download_dir = "Point_downloads"
    if not os.path.exists(download_dir):
        return []
    
    l2_files = []
    for file in os.listdir(download_dir):
        if file.endswith(".csv") and ("L2a_" in file or "L2b_" in file):
            l2_files.append(os.path.join(download_dir, file))
    
    return l2_files

if __name__ == "__main__":
    print("=== EGMS L2 Location Name Generator ===")
    
    # Check if specific file exists
    if os.path.exists(INPUT_CSV_PATH):
        print(f"Using specified input file: {INPUT_CSV_PATH}")
        print("Adding location names to points...")
        enrich_csv_with_locations(INPUT_CSV_PATH)
    else:
        print(f"Specified file not found: {INPUT_CSV_PATH}")
        
        # Look for any L2 files
        l2_files = find_l2_files()
        if l2_files:
            print(f"Found {len(l2_files)} L2 file(s):")
            for i, file in enumerate(l2_files, 1):
                print(f"  {i}. {os.path.basename(file)}")
            
            choice = input(f"\nEnter file number to process (1-{len(l2_files)}), or 'all' to process all files: ")
            
            if choice.lower() == 'all':
                for file in l2_files:
                    print(f"\nProcessing: {os.path.basename(file)}")
                    enrich_csv_with_locations(file)
            else:
                try:
                    file_idx = int(choice) - 1
                    if 0 <= file_idx < len(l2_files):
                        print(f"\nProcessing: {os.path.basename(l2_files[file_idx])}")
                        enrich_csv_with_locations(l2_files[file_idx])
                    else:
                        print("Invalid file number")
                except ValueError:
                    print("Invalid input")
        else:
            print("No L2 CSV files found in Point_downloads directory")
            print("Please download L2 files first or update the INPUT_CSV_PATH") 