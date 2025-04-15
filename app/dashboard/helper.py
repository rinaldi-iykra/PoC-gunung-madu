from app import app
import ee
import os
import json
import joblib
import numpy as np
from shapely.geometry import Polygon
from pyproj import Geod

class DashboardHelper:
    base_dir = app.config['BASE_DIR']
    service_account = ''
    key_path = ''
    kml_path = ''

    def __init__(self):
        self.service_account = app.config['EE_SERVICE_ACCOUNT']
        self.key_path = os.path.join(
            self.base_dir,
            app.config['EE_KEY_PATH']
        )
        self.kml_path = os.path.join(
            self.base_dir,
            app.config['KML_PATH']
        )

        credentials = ee.ServiceAccountCredentials(self.service_account, self.key_path)
        ee.Initialize(credentials)

    def load_kml(self):
        with open(self.kml_path, "r", encoding="utf-8") as f:
            json_data = json.load(f)

        polygon_data = []

        for item in json_data.get("data", []):
            name = item.get("name", "Unnamed")
            coords = item.get("coordinates", [])

            polygon_data.append({
                "name": name,
                "coordinates": coords
            })

        return polygon_data
    
    def calculate_wide(self, location=0):
        polygons = self.load_kml()
        first_poly = polygons[location]
        coords = first_poly["coordinates"]
        lats, lons = zip(*[(lat, lon) for lon, lat in coords])

        geod = Geod(ellps="WGS84")
        area, _ = geod.polygon_area_perimeter(lons, lats)
        area = abs(area)
        hectares = area / 10_000

        return hectares
    
    def setup_date(self, period: str):
        period_map = {
            "Q1": ("01-01", "03-31"),
            "Q2": ("04-01", "06-30"),
            "Q3": ("07-01", "09-30"),
            "Q4": ("10-01", "12-31"),
        }
        return period_map.get(period.upper(), ("01-01", "03-31"))

    def calculate_ndvi(self, year: str = '2019', period: str = 'Q1', location = 0):
        polygons = self.load_kml()
        first_poly = polygons[location]
        coords = first_poly["coordinates"]
        area = ee.Geometry.Polygon([coords])

        start_suffix, end_suffix = self.setup_date(period)
        start_date = f"{year}-{start_suffix}"
        end_date = f"{year}-{end_suffix}"

        collection = ee.ImageCollection('COPERNICUS/S2') \
            .filterDate(start_date, end_date) \
            .filterBounds(area) \
            .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20)) \
            .select(['B8', 'B4'])

        if collection.size().getInfo() == 0:
            print("No Sentinel-2 data found for this period and area.")
            return None
        image = collection.median()

        # Hitung NDVI
        ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')
        mean_dict = ndvi.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=area,
            scale=10,
            maxPixels=1e9
        )
        ndvi_value = mean_dict.getInfo().get('NDVI')

        return ndvi_value
    
    def download_ndvi(self, year: str = '2019', period: str = 'Q1'):
        polygons = self.load_kml()
        first_poly = polygons[0]
        coords = first_poly["coordinates"]
        area = ee.Geometry.Polygon([coords])

        start_suffix, end_suffix = self.setup_date(period)
        start_date = f"{year}-{start_suffix}"
        end_date = f"{year}-{end_suffix}"

        collection = ee.ImageCollection('COPERNICUS/S2') \
            .filterDate(start_date, end_date) \
            .filterBounds(area) \
            .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20)) \
            .select(['B8', 'B4'])

        if collection.size().getInfo() == 0:
            print("No Sentinel-2 data found for this period and area.")
            return None

        image = collection.median()

        # Hitung NDVI
        ndvi = image.normalizedDifference(['B8', 'B4']).rename('NDVI')

        # Export as image download URL (PNG)
        url = ndvi.visualize(min=0.0, max=1.0, palette=['white', 'green']) \
            .getDownloadURL({
                'scale': 10,
                'region': area,
                'format': 'GEO_TIFF'
            })

        print("Download NDVI image URL:", url)
        return url
    
    def calculate_harvest_day(self, ndvi):
        model = joblib.load('ndvi_to_harvest_days.pkl')
        
        all_tree_preds = [tree.predict(np.array([[ndvi]]))[0] for tree in model.estimators_]
        days_remaining = np.mean(all_tree_preds)
        std_dev = np.std(all_tree_preds)
        confidence_score = max(0, min(100, 100 - (std_dev / days_remaining * 100)))

        return days_remaining, confidence_score
    
    def calculate_yield(self, year, hectare):
        model = joblib.load('yield_per_hectare_model.pkl')
        poly = joblib.load('year_poly_transform.pkl')

        year_poly = poly.transform([[year]])
        yield_per_hectare = model.predict(year_poly)[0]
        total_yield = yield_per_hectare * hectare

        return total_yield
    