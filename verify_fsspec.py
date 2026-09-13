import fsspec
import tifffile
import time
import utm

def test_fsspec():
    url = "https://sentinel-cogs.s3.us-west-2.amazonaws.com/sentinel-s2-l2a-cogs/43/R/GM/2026/6/S2B_43RGM_20260617_0_L2A/B04.tif"
    lat, lon = 28.53, 77.39
    
    start = time.time()
    
    # Use fsspec to stream over HTTP
    with fsspec.open(url, mode='rb', cache_type='blockcache', block_size=256*1024) as f:
        with tifffile.TiffFile(f) as tif:
            page = tif.pages[0]
            
            tie = page.tags.get('ModelTiepointTag').value
            scale = page.tags.get('ModelPixelScaleTag').value
            
            easting, northing, zone, letter = utm.from_latlon(lat, lon)
            tie_x, tie_y = tie[3], tie[4]
            sx, sy = scale[0], scale[1]
            
            pixel_col = int((easting - tie_x) / sx)
            pixel_row = int((tie_y - northing) / sy)
            
            r_min = max(0, pixel_row - 25)
            r_max = min(page.shape[0], pixel_row + 25)
            c_min = max(0, pixel_col - 25)
            c_max = min(page.shape[1], pixel_col + 25)
            
            # Read only the required chunk via zarr (or asarray)
            # asarray() will attempt to load the chunks covering the slice
            data = page.asarray()[r_min:r_max, c_min:c_max]
            
            print(f"Extracted shape: {data.shape}")
            print(f"Median value: {data.mean()}")
            
    print(f"Time taken: {time.time() - start:.2f} seconds")

if __name__ == '__main__':
    test_fsspec()
