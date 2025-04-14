import ee
import datetime

SERVICE_ACCOUNT = 'ee-service@iykra-online.iam.gserviceaccount.com'
KEY_PATH = 'ee-service-credential.json'

credentials = ee.ServiceAccountCredentials(SERVICE_ACCOUNT, KEY_PATH)
ee.Initialize(credentials)

def get_ndvi_peak(lat: float, lon: float, radius: int = 5000, year: int = 2023):
    start = datetime.date(year, 1, 1)
    end = datetime.date(year, 12, 31)
    point = ee.Geometry.Point([lon, lat])
    roi = point.buffer(radius)

    s2 = (
        ee.ImageCollection("COPERNICUS/S2_SR")
        .filterBounds(roi)
        .filterDate(str(start), str(end))
        .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 20))
        .map(lambda img: img.normalizedDifference(["B8", "B4"]).rename("NDVI"))
    )

    ndvi_max_image = s2.max()
    ndvi_max_value = ndvi_max_image.reduceRegion(
        reducer=ee.Reducer.max(),
        geometry=roi,
        scale=10,
        maxPixels=1e9
    )

    return ndvi_max_value.getInfo()["NDVI"]

# Contoh pemanggilan
lat, lon = -5.2, 105.3
print(get_ndvi_peak(lat, lon))
