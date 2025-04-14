from app import app
import ee
import os
import json
import joblib

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
    
    def setup_date(self, period: str):
        period_map = {
            "Q1": ("01-01", "03-31"),
            "Q2": ("04-01", "06-30"),
            "Q3": ("07-01", "09-30"),
            "Q4": ("10-01", "12-31"),
        }
        return period_map.get(period.upper(), ("01-01", "03-31"))

    def calculate_ndvi(self, year: str = '2019', period: str = 'Q1'):
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
        mean_dict = ndvi.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=area,
            scale=10,
            maxPixels=1e9
        )
        ndvi_value = mean_dict.getInfo().get('NDVI')

        return ndvi_value

    def calculate_ndwi(self):
        pass

    def calculate_temperature(self, year: str = '2019', period: str = 'Q1'):

        polygons = self.load_kml()
        first_poly = polygons[0]
        coords = first_poly["coordinates"]
        area = ee.Geometry.Polygon([coords])

        start_suffix, end_suffix = self.setup_date(period)
        start_date = f"{year}-{start_suffix}"
        end_date = f"{year}-{end_suffix}"

        # Ambil koleksi citra
        collection = ee.ImageCollection('MODIS/006/MOD11A2') \
            .filterDate(start_date, end_date) \
            .filterBounds(area) \
            .select('LST_Day_1km')

        # Cek apakah koleksi punya gambar
        size = collection.size().getInfo()
        if size == 0:
            print("No MODIS LST data found for this period and area.")
            return None

        # Hitung rata-rata & konversi ke Celsius
        image = collection.mean()
        lst_celsius = image.multiply(0.02).subtract(273.15).rename('LST_Celsius')

        mean_dict = lst_celsius.reduceRegion(
            reducer=ee.Reducer.mean(),
            geometry=area,
            scale=1000,
            maxPixels=1e9
        )

        temperature_value = mean_dict.getInfo().get('LST_Celsius')
        return temperature_value



    def calculate_cgdd(self, temp):
        base_sugarcane_temp = 18 # 18 degree celcius
        result = (temp - base_sugarcane_temp)
        return "%.4f" % round(result, 4)

    def calculate_prediction(self, ndvi, cgdd):
        model = joblib.load('harvest_predictor.joblib')
        predicted_days = model.predict([[ndvi, cgdd]])
        return int(predicted_days)