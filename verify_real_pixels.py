import os
import requests
import json
import numpy as np
import tifffile
import utm
from pystac_client import Client

def download_file(url, local_path):
    if not os.path.exists(local_path):
        print(f"Downloading {url}...")
        r = requests.get(url, stream=True)
        if r.status_code == 200:
            with open(local_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"Saved to {local_path} ({os.path.getsize(local_path)} bytes)")
        else:
            print(f"Failed to download: {r.status_code}")
            return False
    return True

def test():
    client = Client.open('https://earth-search.aws.element84.com/v1')
    
    # Event centroid in India
    lat, lon = 28.53, 77.39 # near Delhi
    bbox = [lon - 0.02, lat - 0.02, lon + 0.02, lat + 0.02]
    
    search = client.search(
        collections=['sentinel-2-l2a'],
        bbox=bbox,
        datetime="2026-06-15T00:00:00Z/2026-07-15T00:00:00Z",
        limit=5
    )
    items = list(search.items())
    items.sort(key=lambda x: x.properties.get('eo:cloud_cover', 100))
    item = items[0]
    
    print(f"Selected item: {item.id} with cloud cover {item.properties.get('eo:cloud_cover')}")
    
    b04_asset = item.assets.get('red') or item.assets.get('B04')
    url = b04_asset.href
    
    os.makedirs('data/interim/sentinel2/cache', exist_ok=True)
    local_path = f"data/interim/sentinel2/cache/{item.id}_B04.tif"
    
    if download_file(url, local_path):
        with tifffile.TiffFile(local_path) as tif:
            page = tif.pages[0]
            print("Dimensions:", page.shape)
            print("Dtype:", page.dtype)
            
            # The ModelTiepointTag is (0, 0, 0, x, y, z)
            # The ModelPixelScaleTag is (sx, sy, sz)
            # So geotransform is roughly: 
            # x_coord = tie_x + pixel_col * sx
            # y_coord = tie_y - pixel_row * sy
            
            tiepoints = page.tags.get('ModelTiepointTag')
            pixelscale = page.tags.get('ModelPixelScaleTag')
            
            if tiepoints and pixelscale:
                tie = tiepoints.value
                scale = pixelscale.value
                print("Georeferencing Tiepoints:", tie)
                print("Georeferencing Scale:", scale)
                
                # Convert lat/lon to UTM
                easting, northing, zone_number, zone_letter = utm.from_latlon(lat, lon)
                print(f"Target UTM: E:{easting}, N:{northing}")
                
                tie_x, tie_y = tie[3], tie[4]
                sx, sy = scale[0], scale[1]
                
                # pixel = (coord - origin) / scale
                pixel_col = int((easting - tie_x) / sx)
                pixel_row = int((tie_y - northing) / sy)
                
                print(f"Event falls in pixel: {pixel_col}, {pixel_row}")
                
                # Extract small window (e.g. 50x50 pixels around center)
                r_min = max(0, pixel_row - 25)
                r_max = min(page.shape[0], pixel_row + 25)
                c_min = max(0, pixel_col - 25)
                c_max = min(page.shape[1], pixel_col + 25)
                
                # read the whole array, or just read the slice!
                # with large tiffs, tifffile can read subset via zarr or asarray if we do it carefully
                data = page.asarray()[r_min:r_max, c_min:c_max]
                print(f"Extracted window shape: {data.shape}")
                print(f"Median B04 value: {np.median(data)}")
                print(f"Min B04 value: {np.min(data)}")
                print(f"Max B04 value: {np.max(data)}")

if __name__ == '__main__':
    test()
