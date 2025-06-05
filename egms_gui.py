import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import zipfile
import os
from io import BytesIO
from time import sleep
import threading
from curl_cffi import requests as curl_requests

# Configuration
BASE_URL_L3 = "https://egms.land.copernicus.eu/insar-api/archive/download/EGMS_{data_type}_E{e}N{n}_100km_{d}_{year}_1.zip?id={id}"
BASE_URL_L2 = "https://egms.land.copernicus.eu/insar-api/archive/download/EGMS_{data_type}_{relative_orbit}_{burst_cycle}_{swath}_{polarization}_{year}_1.zip?id={id}"
DISPLACEMENTS = ["E", "U"]
DOWNLOAD_BASE = "Point_downloads"
DELAY = 3.0  # seconds between requests
DEFAULT_YEAR = "2019_2023"
DEFAULT_ID = "fcf61f768a6141ca81d6e4851c86cf89"

class EGMSApp:
    def __init__(self, root):
        self.root = root
        self.root.title("EGMSweb - Desktop Version")
        self.root.geometry("1200x800")
        
        # Variables
        self.level_var = tk.StringVar(value="L3")
        self.download_type_var = tk.StringVar(value="Single File")
        self.displacement_var = tk.StringVar(value="E")
        
        # L2 Parameters
        self.burst_cycle_var = tk.StringVar(value="0716")
        self.polarization_var = tk.StringVar(value="VV")
        self.relative_orbit_var = tk.StringVar(value="052")
        self.swath_var = tk.StringVar(value="IW2")
        
        # L3 Parameters
        self.north_var = tk.IntVar(value=31)
        self.east_var = tk.IntVar(value=32)
        
        # Common Parameters
        self.year_var = tk.StringVar(value=DEFAULT_YEAR)
        self.token_var = tk.StringVar(value=DEFAULT_ID)
        
        # Batch Parameters for L3
        self.min_north_var = tk.IntVar(value=25)
        self.max_north_var = tk.IntVar(value=26)
        self.min_east_var = tk.IntVar(value=10)
        self.max_east_var = tk.IntVar(value=11)
        
        # Batch Parameters for L2
        self.min_rel_orbit_var = tk.IntVar(value=50)
        self.max_rel_orbit_var = tk.IntVar(value=52)
        self.min_burst_cycle_var = tk.IntVar(value=715)
        self.max_burst_cycle_var = tk.IntVar(value=717)
        
        self.setup_ui()
        self.update_parameter_section()
        
    def setup_ui(self):
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="🌍 EGMSweb - Desktop Version", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        # Subtitle
        subtitle_label = ttk.Label(main_frame, text="Developed by Dr. Abidhan Bardhan and Salmen Abbes")
        subtitle_label.grid(row=1, column=0, columnspan=2, pady=(0, 20))
        
        # Level and Download Type Selection Frame
        selection_frame = ttk.Frame(main_frame)
        selection_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        selection_frame.columnconfigure(0, weight=1)
        selection_frame.columnconfigure(1, weight=1)
        
        # Level Selection
        level_frame = ttk.LabelFrame(selection_frame, text="Select Level", padding="10")
        level_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        for i, level in enumerate(["L2A", "L2B", "L3"]):
            ttk.Radiobutton(level_frame, text=level, variable=self.level_var, 
                           value=level, command=self.update_parameter_section).grid(row=0, column=i, padx=5)
        
        # Download Type Selection
        download_frame = ttk.LabelFrame(selection_frame, text="Choose Download Type", padding="10")
        download_frame.grid(row=0, column=1, sticky=(tk.W, tk.E))
        
        for i, dtype in enumerate(["Single File", "Batch Download"]):
            ttk.Radiobutton(download_frame, text=dtype, variable=self.download_type_var, 
                           value=dtype, command=self.update_parameter_section).grid(row=0, column=i, padx=5)
        
        # Main content area
        content_frame = ttk.Frame(main_frame)
        content_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=1)
        content_frame.rowconfigure(0, weight=1)
        
        # Left panel - Parameters and Download
        left_frame = ttk.Frame(content_frame)
        left_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        left_frame.columnconfigure(0, weight=1)
        
        # Parameters frame (will be populated dynamically)
        self.params_frame = ttk.LabelFrame(left_frame, text="Parameters", padding="10")
        self.params_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        self.params_frame.columnconfigure(0, weight=1)
        
        # Download button frame
        button_frame = ttk.Frame(left_frame)
        button_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        button_frame.columnconfigure(0, weight=1)
        
        self.download_button = ttk.Button(button_frame, text="Download", 
                                         command=self.start_download, state=tk.NORMAL)
        self.download_button.grid(row=0, column=0, pady=5)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(button_frame, variable=self.progress_var, 
                                           maximum=100, length=300)
        self.progress_bar.grid(row=1, column=0, pady=5, sticky=(tk.W, tk.E))
        
        # Progress label
        self.progress_label = ttk.Label(button_frame, text="Ready")
        self.progress_label.grid(row=2, column=0, pady=5)
        
        # Right panel - Information and Status
        right_frame = ttk.Frame(content_frame)
        right_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        right_frame.columnconfigure(0, weight=1)
        right_frame.rowconfigure(1, weight=1)
        
        # Information frame
        info_frame = ttk.LabelFrame(right_frame, text="About EGMS Data", padding="10")
        info_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        info_text = """The European Ground Motion Service (EGMS) provides information about ground movements across Europe.

Data Types:
• L2a: Basic processing level with SAR geometry parameters
• L2b: Intermediate processing level with SAR geometry parameters  
• L3: Advanced processing level with geographic coordinates

L2A/L2B Parameters:
• Relative Orbit: SAR satellite orbit number (e.g., 052)
• Burst Cycle: Timing cycle identifier (e.g., 0716)
• Swath: Interferometric Wide (IW) swath number (IW1, IW2, IW3)
• Polarization: Radar wave polarization (VV, VH, HH, HV)

L3 Parameters:
• E/N Coordinates: Geographic tile coordinates (100x100 km tiles)
• Displacement Types:
  - E: East-West displacement
  - U: Up-Down displacement

The data is organized in tiles with different coordinate systems based on processing level."""
        
        info_label = ttk.Label(info_frame, text=info_text, justify=tk.LEFT, wraplength=400)
        info_label.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Status frame
        status_frame = ttk.LabelFrame(right_frame, text="Download Status", padding="10")
        status_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        status_frame.columnconfigure(0, weight=1)
        status_frame.rowconfigure(0, weight=1)
        
        # Status text area
        self.status_text = scrolledtext.ScrolledText(status_frame, width=50, height=15, 
                                                    wrap=tk.WORD, state=tk.DISABLED)
        self.status_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
    def update_parameter_section(self):
        # Clear existing parameters
        for widget in self.params_frame.winfo_children():
            widget.destroy()
        
        level = self.level_var.get()
        download_type = self.download_type_var.get()
        
        if level in ["L2A", "L2B"]:
            self.setup_l2_parameters(download_type)
        else:  # L3
            self.setup_l3_parameters(download_type)
    
    def setup_l2_parameters(self, download_type):
        if download_type == "Single File":
            # Single file L2 parameters
            params_grid = ttk.Frame(self.params_frame)
            params_grid.grid(row=0, column=0, sticky=(tk.W, tk.E))
            params_grid.columnconfigure((0, 1, 2, 3), weight=1)
            
            # Row 1: L2 specific parameters
            ttk.Label(params_grid, text="Burst Cycle:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
            ttk.Entry(params_grid, textvariable=self.burst_cycle_var, width=10).grid(row=1, column=0, padx=5, pady=2)
            
            ttk.Label(params_grid, text="Polarization:").grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
            ttk.Combobox(params_grid, textvariable=self.polarization_var, 
                        values=["VV", "VH", "HH", "HV"], width=8, state="readonly").grid(row=1, column=1, padx=5, pady=2)
            
            ttk.Label(params_grid, text="Relative Orbit:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=2)
            ttk.Entry(params_grid, textvariable=self.relative_orbit_var, width=10).grid(row=1, column=2, padx=5, pady=2)
            
            ttk.Label(params_grid, text="Swath:").grid(row=0, column=3, sticky=tk.W, padx=5, pady=2)
            ttk.Combobox(params_grid, textvariable=self.swath_var, 
                        values=["IW1", "IW2", "IW3"], width=8, state="readonly").grid(row=1, column=3, padx=5, pady=2)
            
            # Row 2: Common parameters
            common_frame = ttk.Frame(self.params_frame)
            common_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
            common_frame.columnconfigure((0, 1), weight=1)
            
            ttk.Label(common_frame, text="Year Range:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
            ttk.Combobox(common_frame, textvariable=self.year_var, 
                        values=["2018_2022", "2019_2023", "2020_2024"], state="readonly").grid(row=1, column=0, padx=5, pady=2, sticky=(tk.W, tk.E))
            
            ttk.Label(common_frame, text="Token:").grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
            ttk.Entry(common_frame, textvariable=self.token_var).grid(row=1, column=1, padx=5, pady=2, sticky=(tk.W, tk.E))
            
        else:  # Batch Download
            # Batch L2 parameters
            batch_frame = ttk.Frame(self.params_frame)
            batch_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
            batch_frame.columnconfigure((0, 1), weight=1)
            
            # Orbit range
            orbit_frame = ttk.LabelFrame(batch_frame, text="Relative Orbit Range", padding="5")
            orbit_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5), pady=2)
            
            ttk.Label(orbit_frame, text="Min:").grid(row=0, column=0)
            ttk.Spinbox(orbit_frame, from_=1, to=999, textvariable=self.min_rel_orbit_var, width=10).grid(row=0, column=1, padx=5)
            ttk.Label(orbit_frame, text="Max:").grid(row=0, column=2)
            ttk.Spinbox(orbit_frame, from_=1, to=999, textvariable=self.max_rel_orbit_var, width=10).grid(row=0, column=3, padx=5)
            
            # Burst cycle range
            burst_frame = ttk.LabelFrame(batch_frame, text="Burst Cycle Range", padding="5")
            burst_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2)
            
            ttk.Label(burst_frame, text="Min:").grid(row=0, column=0)
            ttk.Spinbox(burst_frame, from_=1, to=9999, textvariable=self.min_burst_cycle_var, width=10).grid(row=0, column=1, padx=5)
            ttk.Label(burst_frame, text="Max:").grid(row=0, column=2)
            ttk.Spinbox(burst_frame, from_=1, to=9999, textvariable=self.max_burst_cycle_var, width=10).grid(row=0, column=3, padx=5)
            
            # Selection note
            note_label = ttk.Label(batch_frame, text="Note: Batch download will try all combinations of VV polarization and IW1,IW2,IW3 swaths", 
                                 foreground="blue", font=("Arial", 8))
            note_label.grid(row=1, column=0, columnspan=2, pady=5)
    
    def setup_l3_parameters(self, download_type):
        if download_type == "Single File":
            # Single file L3 parameters
            params_grid = ttk.Frame(self.params_frame)
            params_grid.grid(row=0, column=0, sticky=(tk.W, tk.E))
            params_grid.columnconfigure((0, 1, 2), weight=1)
            
            # Row 1: Coordinates and displacement
            ttk.Label(params_grid, text="North:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
            ttk.Spinbox(params_grid, from_=9, to=55, textvariable=self.north_var, width=10).grid(row=1, column=0, padx=5, pady=2)
            
            ttk.Label(params_grid, text="East:").grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
            ttk.Spinbox(params_grid, from_=9, to=65, textvariable=self.east_var, width=10).grid(row=1, column=1, padx=5, pady=2)
            
            ttk.Label(params_grid, text="Displacement:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=2)
            displacement_frame = ttk.Frame(params_grid)
            displacement_frame.grid(row=1, column=2, padx=5, pady=2)
            
            for i, disp in enumerate(["E", "U", "Both"]):
                ttk.Radiobutton(displacement_frame, text=disp, variable=self.displacement_var, 
                               value=disp).grid(row=i, column=0, sticky=tk.W)
            
            # Row 2: Common parameters
            common_frame = ttk.Frame(self.params_frame)
            common_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
            common_frame.columnconfigure((0, 1), weight=1)
            
            ttk.Label(common_frame, text="Year Range:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
            ttk.Combobox(common_frame, textvariable=self.year_var, 
                        values=["2018_2022", "2019_2023", "2020_2024"], state="readonly").grid(row=1, column=0, padx=5, pady=2, sticky=(tk.W, tk.E))
            
            ttk.Label(common_frame, text="Token:").grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
            ttk.Entry(common_frame, textvariable=self.token_var).grid(row=1, column=1, padx=5, pady=2, sticky=(tk.W, tk.E))
            
        else:  # Batch Download
            # Batch L3 parameters
            batch_frame = ttk.Frame(self.params_frame)
            batch_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
            batch_frame.columnconfigure((0, 1), weight=1)
            
            # North range
            north_frame = ttk.LabelFrame(batch_frame, text="North Range", padding="5")
            north_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 5), pady=2)
            
            ttk.Label(north_frame, text="Min:").grid(row=0, column=0)
            ttk.Spinbox(north_frame, from_=9, to=55, textvariable=self.min_north_var, width=10).grid(row=0, column=1, padx=5)
            ttk.Label(north_frame, text="Max:").grid(row=0, column=2)
            ttk.Spinbox(north_frame, from_=9, to=55, textvariable=self.max_north_var, width=10).grid(row=0, column=3, padx=5)
            
            # East range
            east_frame = ttk.LabelFrame(batch_frame, text="East Range", padding="5")
            east_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2)
            
            ttk.Label(east_frame, text="Min:").grid(row=0, column=0)
            ttk.Spinbox(east_frame, from_=9, to=65, textvariable=self.min_east_var, width=10).grid(row=0, column=1, padx=5)
            ttk.Label(east_frame, text="Max:").grid(row=0, column=2)
            ttk.Spinbox(east_frame, from_=9, to=65, textvariable=self.max_east_var, width=10).grid(row=0, column=3, padx=5)
            
            # Displacement choice for batch
            disp_frame = ttk.LabelFrame(batch_frame, text="Displacement Type", padding="5")
            disp_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
            
            for i, disp in enumerate(["E", "U", "Both"]):
                ttk.Radiobutton(disp_frame, text=disp, variable=self.displacement_var, 
                               value=disp).grid(row=0, column=i, padx=10)
    
    def log_status(self, message):
        """Add a message to the status log"""
        self.status_text.config(state=tk.NORMAL)
        self.status_text.insert(tk.END, f"{message}\n")
        self.status_text.see(tk.END)
        self.status_text.config(state=tk.DISABLED)
        self.root.update_idletasks()
    
    def update_progress(self, value, text=""):
        """Update progress bar and label"""
        self.progress_var.set(value)
        if text:
            self.progress_label.config(text=text)
        self.root.update_idletasks()
    
    def download_tile(self, e, n, d, data_type="L3", year=DEFAULT_YEAR, id=DEFAULT_ID, 
                     relative_orbit=None, burst_cycle=None, swath=None, polarization=None):
        """Download a single tile with given coordinates and displacement type"""
        
        if data_type == "L3":
            tile_code = f"E{e}N{n}"
            filename_prefix = f"EGMS_{data_type}_{tile_code}_100km_{d}_{year}_1"
            url = BASE_URL_L3.format(data_type=data_type, e=e, n=n, d=d, year=year, id=id)
        else:
            if not all([relative_orbit, burst_cycle, swath, polarization]):
                self.log_status(f"Missing parameters for {data_type} download")
                return False
            
            filename_prefix = f"EGMS_{data_type}_{relative_orbit}_{burst_cycle}_{swath}_{polarization}_{year}_1"
            url = BASE_URL_L2.format(
                data_type="L2a" if data_type == "L2A" else "L2b", 
                relative_orbit=relative_orbit, 
                burst_cycle=burst_cycle, 
                swath=swath, 
                polarization=polarization, 
                year=year, 
                id=id
            )
        
        try:
            response = curl_requests.get(url, timeout=300)
            self.log_status(f"Response for {filename_prefix}: {response.status_code}")
            
            if response.status_code != 200:
                self.log_status(f"Failed to download {filename_prefix}")
                return False
            
            # Create download directory if it doesn't exist
            os.makedirs(DOWNLOAD_BASE, exist_ok=True)
            
            # Read zip from memory
            with zipfile.ZipFile(BytesIO(response.content)) as z:
                for name in z.namelist():
                    if name.endswith(".csv") and filename_prefix in name:
                        z.extract(name, path=DOWNLOAD_BASE)
                        self.log_status(f"Extracted {name}")
                        return True
            
            self.log_status(f"No matching CSV found in the downloaded zip for {filename_prefix}")
            return False
        
        except Exception as e:
            self.log_status(f"Error downloading {filename_prefix}: {e}")
            return False
    
    def start_download(self):
        """Start the download process in a separate thread"""
        self.download_button.config(state=tk.DISABLED)
        self.progress_var.set(0)
        self.log_status("Starting download...")
        
        # Start download in a separate thread to prevent GUI freezing
        thread = threading.Thread(target=self.download_worker)
        thread.daemon = True
        thread.start()
    
    def download_worker(self):
        """Worker method for downloading - runs in separate thread"""
        try:
            level = self.level_var.get()
            download_type = self.download_type_var.get()
            year = self.year_var.get()
            token = self.token_var.get()
            
            if download_type == "Single File":
                if level == "L3":
                    self.download_single_l3(year, token)
                else:
                    self.download_single_l2(level, year, token)
            else:  # Batch Download
                if level == "L3":
                    self.download_batch_l3(year, token)
                else:
                    self.download_batch_l2(level, year, token)
                    
        except Exception as e:
            self.log_status(f"Download error: {e}")
        finally:
            # Re-enable download button
            self.root.after(0, lambda: self.download_button.config(state=tk.NORMAL))
            self.root.after(0, lambda: self.update_progress(100, "Complete"))
    
    def download_single_l3(self, year, token):
        """Download single L3 file"""
        north = self.north_var.get()
        east = self.east_var.get()
        displacement = self.displacement_var.get()
        
        if displacement == "Both":
            displacements = ["E", "U"]
        else:
            displacements = [displacement]
        
        total_tasks = len(displacements)
        for i, d in enumerate(displacements):
            progress = (i / total_tasks) * 100
            self.root.after(0, lambda p=progress, text=f"Downloading {d} displacement data...": 
                          self.update_progress(p, text))
            
            success = self.download_tile(east, north, d, "L3", year, token)
            if success:
                self.log_status(f"Successfully downloaded E{east}N{north} {d}")
            else:
                self.log_status(f"Failed to download E{east}N{north} {d}")
            
            sleep(DELAY)
    
    def download_single_l2(self, level, year, token):
        """Download single L2 file"""
        relative_orbit = self.relative_orbit_var.get()
        burst_cycle = self.burst_cycle_var.get()
        swath = self.swath_var.get()
        polarization = self.polarization_var.get()
        
        self.root.after(0, lambda: self.update_progress(50, f"Downloading {level} data..."))
        
        success = self.download_tile(0, 0, "", level, year, token, 
                                   relative_orbit, burst_cycle, swath, polarization)
        if success:
            self.log_status(f"Successfully downloaded {level}_{relative_orbit}_{burst_cycle}_{swath}_{polarization}")
        else:
            self.log_status(f"Failed to download {level}_{relative_orbit}_{burst_cycle}_{swath}_{polarization}")
    
    def download_batch_l3(self, year, token):
        """Download batch L3 files"""
        min_north = self.min_north_var.get()
        max_north = self.max_north_var.get()
        min_east = self.min_east_var.get()
        max_east = self.max_east_var.get()
        displacement = self.displacement_var.get()
        
        if displacement == "Both":
            displacements = ["E", "U"]
        else:
            displacements = [displacement]
        
        total_tasks = (max_east - min_east + 1) * (max_north - min_north + 1) * len(displacements)
        task_count = 0
        
        for e in range(min_east, max_east + 1):
            for n in range(min_north, max_north + 1):
                for d in displacements:
                    task_count += 1
                    progress = (task_count / total_tasks) * 100
                    self.root.after(0, lambda p=progress, text=f"Downloading tile {task_count}/{total_tasks}": 
                                  self.update_progress(p, text))
                    
                    success = self.download_tile(e, n, d, "L3", year, token)
                    if success:
                        self.log_status(f"Successfully downloaded E{e}N{n} {d}")
                    else:
                        self.log_status(f"Failed to download E{e}N{n} {d}")
                    
                    sleep(DELAY)
    
    def download_batch_l2(self, level, year, token):
        """Download batch L2 files"""
        min_orbit = self.min_rel_orbit_var.get()
        max_orbit = self.max_rel_orbit_var.get()
        min_burst = self.min_burst_cycle_var.get()
        max_burst = self.max_burst_cycle_var.get()
        
        # For batch, use predefined combinations
        swaths = ["IW1", "IW2", "IW3"]
        polarizations = ["VV"]
        
        orbit_count = max_orbit - min_orbit + 1
        burst_count = max_burst - min_burst + 1
        total_combinations = orbit_count * burst_count * len(swaths) * len(polarizations)
        
        task_count = 0
        successful = 0
        failed = 0
        
        for rel_orbit in range(min_orbit, max_orbit + 1):
            for burst_cycle in range(min_burst, max_burst + 1):
                for swath in swaths:
                    for polarization in polarizations:
                        task_count += 1
                        progress = (task_count / total_combinations) * 100
                        
                        rel_orbit_str = f"{rel_orbit:03d}"
                        burst_cycle_str = f"{burst_cycle:04d}"
                        
                        self.root.after(0, lambda p=progress, text=f"Downloading {task_count}/{total_combinations}": 
                                      self.update_progress(p, text))
                        
                        success = self.download_tile(0, 0, "", level, year, token, 
                                                   rel_orbit_str, burst_cycle_str, swath, polarization)
                        
                        if success:
                            successful += 1
                            self.log_status(f"✓ Downloaded {level}_{rel_orbit_str}_{burst_cycle_str}_{swath}_{polarization}")
                        else:
                            failed += 1
                            self.log_status(f"✗ Failed {level}_{rel_orbit_str}_{burst_cycle_str}_{swath}_{polarization}")
                        
                        sleep(DELAY)
        
        self.log_status(f"Batch complete! Successful: {successful}, Failed: {failed}")

def main():
    root = tk.Tk()
    app = EGMSApp(root)
    root.mainloop()

if __name__ == "__main__":
    main() 