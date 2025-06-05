# 🌍 EGMS Data Tool

A comprehensive toolkit for downloading and processing European Ground Motion Service (EGMS) data with multiple interfaces: web app, desktop GUI, and command-line tools.

**Developed by Dr. Abidhan Bardhan and Salmen Abbes**

## 📋 Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Project Structure](#project-structure)
- [Usage](#usage)
  - [Web Interface](#web-interface)
  - [Desktop GUI](#desktop-gui)
  - [Command Line Tools](#command-line-tools)
- [Dependencies](#dependencies)
- [Data Types](#data-types)
- [Contributing](#contributing)

## ✨ Features

### 🖥️ **Multiple Interfaces**
- **Web Application**: Browser-based interface with direct file downloads
- **Desktop GUI**: Native tkinter application for offline use
- **CLI Tools**: Command-line scripts for automated workflows

### 📥 **Download Capabilities**
- **L2A/L2B Data**: SAR geometry-based processing levels
- **L3 Data**: Geographic coordinate-based processing level
- **Single File Downloads**: Individual data tiles
- **Batch Downloads**: Multiple files with automatic ZIP packaging
- **Browser Streaming**: Direct downloads without server storage

### 🌍 **Location Processing**
- **Coordinate Transformation**: EPSG:3035 to WGS84 conversion
- **Geocoding**: Automatic location name resolution
- **Progress Tracking**: Real-time progress bars for batch operations

## 🚀 Installation

### Prerequisites
- Python 3.8 or higher
- Internet connection for EGMS API access

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Quick Start
```bash
# Run web interface
streamlit run egms_web.py

# Run desktop GUI
python egms_gui.py

# Run CLI tool
python egms_L3_single.py
```

## 📁 Project Structure

### Core Applications
| File | Type | Description |
|------|------|-------------|
| `egms_web.py` | Web App | Streamlit-based web interface with browser downloads |
| `egms_gui.py` | Desktop GUI | Tkinter native desktop application |

### L3 Data Tools (Geographic Coordinates)
| File | Purpose | Dependencies |
|------|---------|-------------|
| `egms_L3_single.py` | Download single L3 files | curl-cffi |
| `egms_L3_multiple.py` | Batch download L3 files | curl-cffi |
| `egms_L3_locations.py` | Add location names to L3 CSV files | pyproj, geopy, tqdm |

### L2 Data Tools (SAR Geometry)
| File | Purpose | Dependencies |
|------|---------|-------------|
| `egms_L2_single.py` | Download single L2A/L2B files | curl-cffi |
| `egms_L2_multiple.py` | Batch download L2A/L2B files | curl-cffi |
| `egms_L2_locations.py` | Add location names to L2 CSV files | pyproj, geopy, tqdm |

### Configuration
| File | Description |
|------|-------------|
| `requirements.txt` | Python dependencies |
| `README.md` | Project documentation |

## 🎯 Usage

### Web Interface

Launch the web application:
```bash
streamlit run egms_web.py
```

**Features:**
- **Direct Browser Downloads**: Files stream directly to your browser
- **Interactive Parameter Selection**: Dynamic forms based on data type
- **Progress Tracking**: Real-time download progress
- **Automatic ZIP Packaging**: Batch downloads packaged automatically

**How to Use:**
1. Select data level (L2A, L2B, or L3)
2. Choose download type (Single File or Batch)
3. Configure parameters for your data type
4. Click "🔄 Prepare Download" to fetch data
5. Click "💾 Download File" when ready

### Desktop GUI

Launch the desktop application:
```bash
python egms_gui.py
```

**Features:**
- **Native Desktop Interface**: No browser required
- **Threading**: Non-blocking downloads with progress bars
- **Real-time Logging**: Detailed status messages
- **Professional Layout**: Organized parameter sections

### Command Line Tools

#### Single File Downloads
```bash
# L3 single file
python egms_L3_single.py

# L2 single file  
python egms_L2_single.py
```

#### Batch Downloads
```bash
# L3 batch download
python egms_L3_multiple.py

# L2 batch download
python egms_L2_multiple.py
```

#### Location Processing
```bash
# Add locations to L3 data
python egms_L3_locations.py

# Add locations to L2 data
python egms_L2_locations.py
```

### Configuration

Edit the configuration variables in each script:

```python
# Example configuration
YEAR = "2019_2023"  # 2018_2022, 2019_2023, 2020_2024
ID = "your_token_here"
N_COORD = 31
E_COORD = 32
DISPLACEMENT_TYPE = "U"  # "E" for East-West, "U" for Up-Down
```

## 📦 Dependencies

### Required Libraries

| Library | Purpose | Used In | Version |
|---------|---------|---------|---------|
| **streamlit** | Web interface framework | Web app | ≥1.28.0 |
| **curl-cffi** | HTTP requests with CloudFlare bypass | All download tools | ≥0.6.0 |
| **pyproj** | Coordinate system transformations | Location tools | ≥3.6.0 |
| **geopy** | Geocoding services | Location tools | ≥2.4.0 |
| **tqdm** | Progress bars | CLI location tools | ≥4.66.0 |

### Built-in Libraries (No Installation Required)
- **tkinter**: Desktop GUI framework
- **zipfile**: ZIP file handling
- **os**: Operating system interface
- **io**: Input/output utilities
- **time**: Time-related functions
- **csv**: CSV file processing
- **threading**: Thread management

### Dependency Installation
```bash
# Install all dependencies
pip install -r requirements.txt

# Install specific components
pip install streamlit>=1.28.0  # Web interface only
pip install curl-cffi>=0.6.0   # Download tools only
```

## 📊 Data Types

### L2A/L2B Parameters
- **Relative Orbit**: SAR satellite orbit number (e.g., 052)
- **Burst Cycle**: Timing cycle identifier (e.g., 0716)
- **Swath**: Interferometric Wide (IW) swath number (IW1, IW2, IW3)
- **Polarization**: Radar wave polarization (VV, VH, HH, HV)

### L3 Parameters  
- **E/N Coordinates**: Geographic tile coordinates (100x100 km tiles)
- **Displacement Types**:
  - **E**: East-West displacement
  - **U**: Up-Down displacement

### Year Ranges
- **2018_2022**: Historical data
- **2019_2023**: Most recent complete dataset
- **2020_2024**: Latest available data

## 🔧 Advanced Configuration

### Custom Token
Replace the default token in scripts or web interface:
```python
DEFAULT_ID = "your_custom_token_here"
```

### Download Delays
Adjust request delays to respect server limits:
```python
DELAY = 3.0  # seconds between requests
```

### Output Directories
Customize output paths for CLI tools:
```python
DOWNLOAD_BASE = "Point_downloads"
NAMES_DATASETS_DIR = "Point_locations"
```

## 📈 Performance Tips

1. **Use appropriate delays** between requests to avoid overwhelming servers
2. **Start with small batches** to test parameters before large downloads
3. **Monitor network stability** for large batch operations
4. **Use the web interface** for interactive exploration
5. **Use CLI tools** for automated workflows

## 🛠️ Troubleshooting

### Common Issues

**Download Failures:**
- Check internet connection
- Verify token validity
- Ensure parameter combinations exist
- Try different year ranges

**Coordinate Transformation Errors:**
- Verify pyproj installation
- Check coordinate format
- Ensure EPSG support is available

**GUI Not Responding:**
- Check if downloads are running in background
- Wait for current operation to complete
- Restart application if necessary

## 📝 Example Workflows

### Research Data Collection
```bash
# 1. Download L3 data for study area
python egms_L3_multiple.py  # Configure area bounds

# 2. Add location names
python egms_L3_locations.py

# 3. Process results
# Your analysis code here
```

### Quick Data Exploration
```bash
# Use web interface for interactive exploration
streamlit run egms_web.py
```

### Automated Pipeline
```bash
# Batch download with custom parameters
python egms_L2_multiple.py  # Configure in script
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test with different data types
5. Submit a pull request

## 📄 License

This project is developed for research and educational purposes. Please respect the EGMS data usage policies and terms of service.

## 🔗 References

- [European Ground Motion Service (EGMS)](https://egms.land.copernicus.eu/)
- [Copernicus Land Monitoring Service](https://land.copernicus.eu/)

---

**For support or questions, please contact the developers: Dr. Abidhan Bardhan and Salmen Abbes**
