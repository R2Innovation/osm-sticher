"""
OpenStreetMap Tile Stitcher v2
R Square Innovative Software - GPLv3 License
Stitches map tiles into a single high-resolution image
"""

import requests
from PIL import Image
import math
import os
import sys
from tqdm import tqdm

# --- Configuration ---
# 1. Bounding Box Coordinates
fMinLat = 44.80924
fMinLon = -0.64236
fMaxLat = 44.87959
fMaxLon = -0.46795

# 2. Zoom Level
iZoom = 17

# 3. Output Configuration
sOutputFile = "custom_map_zoom17_PROGRESS.png"
sTileDir = "downloaded_tiles_progress"
# ---------------------

def fn_create_directory(sDirectoryPath):
    """Create directory if it doesn't exist"""
    if not os.path.exists(sDirectoryPath):
        os.makedirs(sDirectoryPath)
        print(f"Created directory: {sDirectoryPath}")
    return True

def fn_degrees_to_tile_numbers(fLatDeg, fLonDeg, iZoomLevel):
    """Convert latitude/longitude to tile numbers"""
    fLatRad = math.radians(fLatDeg)
    fN = 2.0 ** iZoomLevel
    iXTile = int((fLonDeg + 180.0) / 360.0 * fN)
    iYTile = int((fN * (1.0 - math.log(math.tan(fLatRad) + 1/math.cos(fLatRad)) / math.pi) / 2.0))
    return (iXTile, iYTile)

def fn_calculate_tile_ranges(fMinLon, fMinLat, fMaxLon, fMaxLat, iZoomLevel):
    """Calculate tile coordinate ranges for the bounding box"""
    iTopTileX, iTopTileY = fn_degrees_to_tile_numbers(fMaxLat, fMinLon, iZoomLevel)
    iBottomTileX, iBottomTileY = fn_degrees_to_tile_numbers(fMinLat, fMaxLon, iZoomLevel)
    
    vTileRangeX = range(iTopTileX, iBottomTileX + 1)
    vTileRangeY = range(iTopTileY, iBottomTileY + 1)
    
    return vTileRangeX, vTileRangeY

def fn_generate_tile_coordinates(vTileRangeX, vTileRangeY):
    """Generate all tile coordinate combinations"""
    vTileCoords = [(x, y) for x in vTileRangeX for y in vTileRangeY]
    return vTileCoords

def fn_generate_tile_url(iZoomLevel, iXTile, iYTile):
    """Generate OpenStreetMap tile URL"""
    sUrl = f"https://tile.openstreetmap.org/{iZoomLevel}/{iXTile}/{iYTile}.png"
    return sUrl

def fn_generate_tile_path(sTileDirectory, iZoomLevel, iXTile, iYTile):
    """Generate file path for tile"""
    sTilePath = os.path.join(sTileDirectory, f"{iZoomLevel}_{iXTile}_{iYTile}.png")
    return sTilePath

def fn_download_tile(sUrl, sTilePath):
    """Download a single tile and save it"""
    try:
        oResponse = requests.get(sUrl, stream=True, 
                                headers={'User-Agent': 'R-Square-MapStitcher/2.0 (contact@rsquareinnovative.com)'})
        oResponse.raise_for_status()
        return oResponse
    except requests.exceptions.RequestException as e:
        print(f"Error downloading tile: {e}")
        return None

def fn_save_tile(oResponse, sTilePath):
    """Save tile image to disk"""
    try:
        oTileImage = Image.open(oResponse.raw)
        oTileImage.save(sTilePath)
        return oTileImage
    except Exception as e:
        print(f"Error saving tile {sTilePath}: {e}")
        return None

def fn_calculate_grid_position(iIndex, iNumTilesY):
    """Calculate grid position for tile placement"""
    iGridX = iIndex // iNumTilesY
    iGridY = iIndex % iNumTilesY
    return iGridX, iGridY

def fn_calculate_paste_coordinates(iGridX, iGridY, iTileSize=256):
    """Calculate paste coordinates for tile"""
    iPasteX = iGridX * iTileSize
    iPasteY = iGridY * iTileSize
    return iPasteX, iPasteY

def fn_create_blank_image(iNumTilesX, iNumTilesY, iTileSize=256):
    """Create blank canvas for final stitched image"""
    iWidth = iNumTilesX * iTileSize
    iHeight = iNumTilesY * iTileSize
    oFullImage = Image.new('RGB', (iWidth, iHeight))
    return oFullImage

def fn_paste_tile(oFullImage, oTileImage, iPasteX, iPasteY):
    """Paste tile onto the full image"""
    oFullImage.paste(oTileImage, (iPasteX, iPasteY))
    return oFullImage

def fn_process_single_tile(iXTile, iYTile, iIndex, iNumTilesY, sTileDirectory, iZoomLevel, oFullImage):
    """Process a single tile: download, save, and place on canvas"""
    sUrl = fn_generate_tile_url(iZoomLevel, iXTile, iYTile)
    sTilePath = fn_generate_tile_path(sTileDirectory, iZoomLevel, iXTile, iYTile)
    
    oResponse = fn_download_tile(sUrl, sTilePath)
    if not oResponse:
        return oFullImage
    
    oTileImage = fn_save_tile(oResponse, sTilePath)
    if not oTileImage:
        return oFullImage
    
    iGridX, iGridY = fn_calculate_grid_position(iIndex, iNumTilesY)
    iPasteX, iPasteY = fn_calculate_paste_coordinates(iGridX, iGridY)
    
    oFullImage = fn_paste_tile(oFullImage, oTileImage, iPasteX, iPasteY)
    return oFullImage

def fn_stitch_tiles(fMinLon, fMinLat, fMaxLon, fMaxLat, iZoomLevel, sOutputPath, sTileDirectory):
    """Main function to orchestrate tile downloading and stitching"""
    # Create directory
    bDirectoryCreated = fn_create_directory(sTileDirectory)
    
    # Calculate tile ranges
    vTileRangeX, vTileRangeY = fn_calculate_tile_ranges(fMinLon, fMinLat, fMaxLon, fMaxLat, iZoomLevel)
    
    # Generate tile coordinates
    vTileCoords = fn_generate_tile_coordinates(vTileRangeX, vTileRangeY)
    
    # Calculate grid dimensions
    iNumTilesX = len(vTileRangeX)
    iNumTilesY = len(vTileRangeY)
    iTotalTiles = iNumTilesX * iNumTilesY
    
    print(f"Starting download of {iTotalTiles} tiles at zoom {iZoomLevel}...")
    
    # Create blank image canvas
    oFullImage = fn_create_blank_image(iNumTilesX, iNumTilesY)
    
    # Process all tiles with progress bar
    for iIndex, (iXTile, iYTile) in enumerate(tqdm(vTileCoords, desc="Downloading Tiles")):
        oFullImage = fn_process_single_tile(iXTile, iYTile, iIndex, iNumTilesY, 
                                           sTileDirectory, iZoomLevel, oFullImage)
    
    # Save final image
    oFullImage.save(sOutputPath)
    print(f"\nSuccessfully saved stitched map to {os.path.abspath(sOutputPath)}")
    return True

def fn_print_usage():
    """Display detailed usage information"""
    sHelpText = """
╔══════════════════════════════════════════════════════════════════════════╗
║                    R Square Map Stitcher v2 - Usage Help                 ║
║                          GPLv3 Licensed Software                         ║
╚══════════════════════════════════════════════════════════════════════════╝

SYNOPSIS:
    python stitcher_v2.py [OPTIONS]

DESCRIPTION:
    Downloads and stitches OpenStreetMap tiles to create custom high-resolution
    map images based on geographical coordinates.

QUICK START:
    1. Edit the configuration variables at the top of the script
    2. Run: python stitcher_v2.py
    3. Find your map in the specified output file

CONFIGURATION OPTIONS (Edit in script):

    # --- Geographical Bounding Box ---
    fMinLat = 44.80924      # Minimum latitude (south)
    fMinLon = -0.64236      # Minimum longitude (west)
    fMaxLat = 44.87959      # Maximum latitude (north)
    fMaxLon = -0.46795      # Maximum longitude (east)

    # --- Zoom Level ---
    iZoom = 17              # Higher = more detail, more tiles (1-19 typical)

    # --- Output Configuration ---
    sOutputFile = "custom_map_zoom17_PROGRESS.png"
    sTileDir = "downloaded_tiles_progress"

COORDINATE FORMAT:
    • Latitude:  -90 to 90 (negative = south)
    • Longitude: -180 to 180 (negative = west)
    • Format:    Decimal degrees (e.g., 44.80924, -0.64236)

ZOOM LEVEL GUIDE:
    • 1-10:     Continental/Country scale
    • 11-15:    City/Town scale
    • 16-19:    Street/Building detail (more tiles, slower)
    • 20+:      Very high detail (may exceed OSM server limits)

OUTPUT:
    • Individual tiles saved in: [sTileDir]/zoom_x_y.png
    • Final stitched image: [sOutputFile]
    • Image dimensions: (tiles_x * 256) x (tiles_y * 256) pixels

COMMAND LINE OPTIONS:
    --help, -h      : Show this help message
    --quick, -q     : Show quick reference guide
    --license, -l   : Show license information
    --run, -r       : Run the stitching process (default)

EXAMPLE USAGE:
    python stitcher_v2.py               # Run with default configuration
    python stitcher_v2.py --help        # Show help
    python stitcher_v2.py --quick       # Quick reference
    python stitcher_v2.py --license     # License information

TROUBLESHOOTING:

    Problem: No tiles downloaded
    Solution: Check internet connection and verify coordinates

    Problem: Final image is too small
    Solution: Increase zoom level or expand bounding box

    Problem: Download is very slow
    Solution: Reduce zoom level or area size

    Problem: Image has black/empty areas
    Solution: Some tile servers may have coverage gaps

LEGAL INFORMATION:
    • This software is licensed under GPLv3
    • Map data © OpenStreetMap contributors
    • Tile usage must comply with OSM policies
    • Commercial use may require additional permissions

CONTACT:
    R Square Innovative Software
    Email: contact@rsquareinnovative.com

For more information: https://operations.osmfoundation.org/policies/tiles/
    """
    print(sHelpText)
    return True

def fn_print_quick_reference():
    """Display quick reference guide"""
    sQuickRef = """
QUICK REFERENCE:

1. GET COORDINATES:
   • Use https://www.openstreetmap.org
   • Right-click → "Show Address"
   • Note lat/lon from URL

2. CALCULATE AREA:
   • Determine NW (top-left) and SE (bottom-right) corners
   • Format: fMinLat, fMinLon, fMaxLat, fMaxLon

3. CHOOSE ZOOM:
   • City overview: 12-14
   • Neighborhood: 15-16
   • Street detail: 17-18
   • Building detail: 19

4. ESTIMATE TILES:
   • Zoom 17: ~1 tile per 0.002° x 0.002°
   • Final size = tiles × 256 pixels

5. RUN:
   python stitcher_v2.py

6. CHECK OUTPUT:
   • Tiles saved in: sTileDir/
   • Final map: sOutputFile
    """
    print(sQuickRef)
    return True

def fn_print_license_info():
    """Display license information"""
    sLicenseInfo = """
GNU GENERAL PUBLIC LICENSE Version 3

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

ADDITIONAL REQUIREMENTS FOR OSM DATA:
• You must credit OpenStreetMap contributors
• You must make it clear that data is available under ODbL
• You must provide a way to access the ODbL
• See: https://www.openstreetmap.org/copyright
    """
    print(sLicenseInfo)
    return True

def fn_main_with_help():
    """Main function with integrated help system"""
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        sArg = sys.argv[1].lower()
        
        if sArg in ['-h', '--help', '/?', 'help']:
            fn_print_usage()
            return True
        elif sArg in ['-q', '--quick']:
            fn_print_quick_reference()
            return True
        elif sArg in ['-l', '--license']:
            fn_print_license_info()
            return True
        elif sArg in ['-r', '--run']:
            # Continue with normal execution
            pass
        else:
            print(f"Unknown option: {sArg}")
            print("Use --help for usage information")
            return False
    
    # Normal execution (no arguments or --run specified)
    print("R Square Map Stitcher v2 - GPLv3 Licensed")
    print("Starting tile stitching process...\n")
    
    bSuccess = fn_stitch_tiles(fMinLon, fMinLat, fMaxLon, fMaxLat, 
                              iZoom, sOutputFile, sTileDir)
    
    if bSuccess:
        print("\nProcess completed successfully!")
    else:
        print("\nProcess encountered errors!")
    
    return bSuccess

# Execute main function
if __name__ == "__main__":
    fn_main_with_help()
