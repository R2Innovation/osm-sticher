# OpenStreetMap Tile Stitcher v2

A Python script developed by R Square Innovative Software that downloads and stitches OpenStreetMap tiles to create custom high-resolution map images. Licensed under GPLv3.

## Features

- Downloads map tiles from OpenStreetMap based on geographical coordinates
- Stitches tiles into a single high-resolution image
- Shows progress bar during download using tqdm
- Saves individual tiles for later use
- Handles download errors gracefully
- Command-line interface with help system
- Configurable bounding box and zoom levels
- Respects OpenStreetMap tile usage policies

## Installation

### Prerequisites
- Python 3.6 or higher
- pip (Python package manager)

### Install Required Libraries

```bash
pip install requests Pillow tqdm
```

Or install from requirements.txt:
```bash
pip install -r requirements.txt
```

## Configuration
Edit the configuration variables at the top of stitcher_v2.py:

```python
# --- Configuration ---
# 1. Bounding Box Coordinates
fMinLat = 44.80924      # Minimum latitude (south)
fMinLon = -0.64236      # Minimum longitude (west)
fMaxLat = 44.87959      # Maximum latitude (north)
fMaxLon = -0.46795      # Maximum longitude (east)

# 2. Zoom Level
iZoom = 17              # Higher = more detail, more tiles (1-19 typical)

# 3. Output Configuration
sOutputFile = "custom_map_zoom17_PROGRESS.png"
sTileDir = "downloaded_tiles_progress"
# ---------------------
```

### Configuration Parameters
| Parameter     | Type    | Description                                        | Example      |
| ------------- | ------- | -------------------------------------------------- | ------------ |
| `fMinLat`     | Float   | Minimum latitude (southern boundary)               | 44.80924     |
| `fMinLon`     | Float   | Minimum longitude (western boundary)               | -0.64236     |
| `fMaxLat`     | Float   | Maximum latitude (northern boundary)               | 44.87959     |
| `fMaxLon`     | Float   | Maximum longitude (eastern boundary)               | -0.46795     |
| `iZoom`       | Integer | Zoom level (1-20, typically 15-18 for good detail) | 17           |
| `sOutputFile` | String  | Final stitched image filename                      | "my_map.png" |
| `sTileDir`    | String  | Directory for individual tiles                     | "tiles/"     |

#### Coordinate Format

**Latitude:**  -90 to 90 degrees (negative = south)<br>
**Longitude:** -180 to 180 degrees (negative = west)<br>
**Format:**    Decimal degrees (e.g., 44.80924, -0.64236)

#### Zoom Level Guide
| **Zoom** | **Description**   | **Tile Count (approx)** | **Best For**    |
|----------|-------------------|-------------------------|-----------------|
| 1-10     | World/Continental | 1-1000                  | Global views    |
| 11-14    | Country/Region    | 1,000-16,000            | Country maps    |
| 15-16    | City              | 16,000-65,000           | City overviews  |
| 17-18    | Street            | 65,000-262,000          | Street detail   |
| 19-20    | Building          | 262,000+                | Building detail |

## Usage

### Command Line Options

```bash
# Show comprehensive help
python stitcher_v2.py --help
python stitcher_v2.py -h

# Show quick reference guide
python stitcher_v2.py --quick
python stitcher_v2.py -q

# Show license information
python stitcher_v2.py --license
python stitcher_v2.py -l

# Run the stitching process (default)
python stitcher_v2.py
python stitcher_v2.py --run
python stitcher_v2.py -r
```

### Basic Usage

1. **Configure the script:** Edit the configuration variables at the top of stitcher_v2.py
2. **Get coordinates:**
     - Visit OpenStreetMap
     - Navigate to your area of interest
     - Right-click → "Show Address" to get coordinates
     - Note the latitude and longitude values
3. **Run the script:**
     ```bash
     python stitcher_v2.py
     ```
4. **Monitor progress:**
     - The script will show a progress bar for tile downloads
     - Individual tiles are saved to the specified directory
     - The final stitched image is created upon completion

### Examples

#### Example 1: Create a map of Bordeaux, France
```python
fMinLat = 44.80924
fMinLon = -0.64236
fMaxLat = 44.87959
fMaxLon = -0.46795
iZoom = 17
sOutputFile = "bordeaux_zoom17.png"
sTileDir = "bordeaux_tiles"
```

#### Example 2: Create a smaller area with higher detail
```python
fMinLat = 44.838  # Central Bordeaux
fMinLon = -0.580
fMaxLat = 44.850
fMaxLon = -0.560
iZoom = 18  # Higher zoom for more detail
```

### Finding Coordinates

- Using [OpenStreetMap.org](https://openstreetmap.org/):
    - Navigate to your location
    - Right-click → "Show Address"
    - Copy coordinates from URL or popup
- Using bounding box tools:
    - [Bounding Box Tool](https://boundingbox.klokantech.com/)
    - [OpenStreetMap Export Tool](https://www.openstreetmap.org/export)

### Output

The script generates two types of output:
1. **Individual Tiles:** Saved in the specified `sTileDir` directory
     - Format: `{zoom}_{x}_{y}.png`
     - Each tile is 256×256 pixels
     - Useful for caching or manual inspection
2. **Final Stitched Image:** Saved as `sOutputFile`
     - Format: PNG (configurable by changing file extension)
     - Dimensions: `(tiles_x × 256) × (tiles_y × 256)` pixels
     - Contains all tiles stitched together in correct geographical order

#### Output Example
```text
project_directory/
├── stitcher_v2.py
├── custom_map_zoom17.png        # Final stitched image
└── downloaded_tiles_progress/   # Individual tiles
    ├── 17_12345_67890.png
    ├── 17_12345_67891.png
    └── ...
```

## Performance Considerations

### Tile Count Estimation

The number of tiles required is calculated as:
```text
tiles_x = (max_lon_tile - min_lon_tile + 1)
tiles_y = (max_lat_tile - min_lat_tile + 1)
total_tiles = tiles_x × tiles_y
```

#### Approximate tile counts for common areas:

- **Small city at zoom 17:** 100-400 tiles (25-100 MB)
- **Medium city at zoom 16:** 400-1,600 tiles (100-400 MB)
- **Large metropolitan area at zoom 15:** 1,600-6,400 tiles (400 MB-1.6 GB)

### Download Time Estimates

- **Standard connection:** ~10-50 tiles per second
- **Large downloads:** Consider adding delays to respect OSM servers
- Total time = `(total_tiles / download_rate)` + processing overhead

### Memory Usage

- Each tile: ~256×256×3 bytes = ~196 KB
- Processing memory: ~(total_tiles × 200 KB) + final image size
- Large areas may require significant RAM

## Compliance and Legal

### OpenStreetMap Tile Usage Policy

This script must comply with OpenStreetMap's Tile Usage Policy:
  - **User-Agent Requirement:** The script includes a proper User-Agent header
  - **Attribution:** You must credit OpenStreetMap contributors
  - **Server Respect:** Do not overload OSM servers
  - **Caching:** Cache tiles locally when possible
  - **Commercial Use:** Commercial use may require additional arrangements

### Required Attribution

When using maps created with this script, you must include:
```text
© OpenStreetMap contributors
```

Or use the provided HTML:
```html
<a href="https://www.openstreetmap.org/copyright">© OpenStreetMap contributors</a>
Rate Limiting Recommendations
```

For large downloads, consider adding delays:
```python
import time
time.sleep(0.1)  # 100ms delay between requests
```

## Troubleshooting

### Common Issues

| **Problem**              | **Possible Cause**                | **Solution**                            |
|--------------------------|-----------------------------------|-----------------------------------------|
| No tiles downloaded      | Invalid coordinates               | Verify coordinates are in correct range |
| Network issues           | Check internet connection         |                                         |
| Partial download         | Server rate limiting              | Add delays between requests             |
| Tile not available       | Some areas may have missing tiles |                                         |
| Final image too small    | Zoom level too low                | Increase zoom level                     |
| Area too small           | Expand bounding box               |                                         |
| Memory error             | Too many tiles                    | Reduce area or zoom level               |
| System memory limit      | Process in smaller batches        |                                         |
| Server errors (HTTP 429) | Too many requests                 | Add longer delays or try later          |

### Error Messages

- **"Error downloading tile":** Network issue or invalid tile coordinate
- **"Error saving tile":** Disk full or permission issue
- **No error but empty image:** Check bounding box coordinates

### Debug Mode
To add debug output, modify the script to print additional information:

```python
# Add debug flag
bDebug = True

if bDebug:
    print(f"Processing tile {iXTile},{iYTile} at URL: {sUrl}")
```
## Development

### Code Structure

The script follows a modular architecture with single-responsibility functions:
 - **Configuration:** Top-level variables
 - **Helper Functions:** Small, focused utility functions
 - **Processing Functions:** Download, save, and stitch operations
 - **Main Function:** Orchestrates the entire process

### Naming Conventions
- Strings: `sVariableName`
- Integers: `iVariableName`
- Floats: `fVariableName`
- Booleans: `bVariableName`
- Vectors/Lists: `vVariableName`
- Objects: `oVariableName`
- Functions: `fn_FunctionName`

### Extending the Script

#### Adding New Tile Servers
```python
def fn_generate_custom_tile_url(iZoomLevel, iXTile, iYTile):
    sUrl = f"https://custom.tile.server/{iZoomLevel}/{iXTile}/{iYTile}.png"
    return sUrl
```

#### Supporting Different Image Formats
```python
# Change in configuration
sOutputFile = "map.jpg"  # or .tiff, .bmp, etc.
```

#### Adding Progress Callbacks
```python
def fn_progress_callback(iCurrent, iTotal):
    print(f"Progress: {iCurrent}/{iTotal} tiles")
```

## License
This software is licensed under the GNU General Public License v3.0 (GPLv3).

```text
Copyright (C) 2023 R Square Innovative Software

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
```

## OpenStreetMap Data License
Map data © OpenStreetMap contributors, licensed under the [Open Data Commons Open Database License](https://opendatacommons.org/licenses/odbl/).

## Support

### Documentation
- [OpenStreetMap Wiki](https://wiki.openstreetmap.org/wiki/Main_Page)
- [OSM Tile Usage Policy](https://operations.osmfoundation.org/policies/tiles/)
- [Slippy Map Tilenames](https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames)

### Community
 - [OpenStreetMap Community](https://community.openstreetmap.org/)
 - [GIS StackExchange](https://gis.stackexchange.com/)

### Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Fully test
5. Submit a pull request

### Testing Checklist
- Coordinates in valid range
- Zoom level appropriate for area
- Output directory writable
- Network connectivity
- Final image matches expected dimensions
- Attribution included in final product

## Changelog

### v2.0
- Added command-line interface with help system
- Implemented progress bars with tqdm
- Modular function architecture
- Enhanced error handling

### v1.0
- Initial release
- Basic tile downloading and stitching
- Configuration via script variables

___________________________________________
**Disclaimer:** This tool is for educational and legitimate mapping purposes. Users are responsible
                for complying with OpenStreetMap's terms of service and all applicable laws.
