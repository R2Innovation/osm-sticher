"""
OpenStreetMap Tile Stitcher v2
R Square Innovative Software - GPLv3 License
Stitches map tiles into a single high-resolution image
"""

import requests
from PIL import Image
import math
import os
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
    vTileRangeY = range(iTopTileX, iBottomTileY + 1)
    
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
                                headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:146.0) Gecko/20100101 Firefox/146.0'})
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

def fn_main():
    """Main execution function"""
    print("R Square Map Stitcher v2 - GPLv3 Licensed")
    print("Starting tile stitching process...")
    
    bSuccess = fn_stitch_tiles(fMinLon, fMinLat, fMaxLon, fMaxLat, 
                               iZoom, sOutputFile, sTileDir)
    
    if bSuccess:
        print("Process completed successfully!")
    else:
        print("Process encountered errors!")
    
    return bSuccess

# Execute main function
if __name__ == "__main__":
    fn_main()