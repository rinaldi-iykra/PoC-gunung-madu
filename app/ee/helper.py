from app import app
import ee
from google.auth import compute_engine
import os
import pandas as pd

class ApiEEHelper:
    service_account = ''
    key_path = ''
    image_collection = 'MODIS/061/MOD13A1'
    ee_service = None
    base_dir = app.config['BASE_DIR']

    def __init__(self):
        self.service_account = app.config['EE_SERVICE_ACCOUNT']
        self.key_path = os.path.join(
            self.base_dir,
            app.config['EE_KEY_PATH']
        )
    
    def calcualte_ndvi_peak(self, lat: float, lon: float, radius: int = 5000, year: int = 2023):
        credentials = ee.ServiceAccountCredentials(
            self.service_account, 
            self.key_path
        )
        ee.Initialize(credentials)

        point = ee.Geometry.Point([lon, lat])
        roi = point.buffer(radius)

        # Koleksi citra MODIS NDVI
        dataset = ee.ImageCollection('MODIS/061/MOD13A1') \
            .filterBounds(roi) \
            .select('NDVI')

        # Fungsi untuk ambil NDVI peak per bulan
        def get_monthly_max(month):
            start_date = ee.Date.fromYMD(year, month, 1)
            end_date = start_date.advance(1, 'month')
            monthly_collection = dataset.filterDate(start_date, end_date)
            monthly_max = monthly_collection.max().clip(roi)
            
            return monthly_max.set({'month': month, 'year': year})

        months = list(range(1, 13))

        # Dapatkan koleksi peak NDVI tiap bulan sebagai ImageCollection
        monthly_peak_ndvi = ee.ImageCollection([get_monthly_max(m) for m in months])

        # Menghitung rata-rata NDVI peak tiap bulan di ROI (opsional)
        def get_monthly_ndvi_mean(image):
            month = image.get('month')
            mean_dict = image.reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=roi,
                scale=500,
                maxPixels=1e9
            )
            ndvi_mean = mean_dict.get('NDVI')
            return ee.Feature(None, {
                'month': month,
                'ndvi_mean': ndvi_mean
            })

        # Buat FeatureCollection berisi nilai NDVI rata-rata tiap bulan
        ndvi_mean_fc = ee.FeatureCollection(monthly_peak_ndvi.map(get_monthly_ndvi_mean))

        # Cetak ke console
        print(ndvi_mean_fc.getInfo())


    def calculate_sentinel_ndvi(self):
        print("SENTINEL2")
        
    def calculate_stage(self):

        file_path = os.path.join(
            self.base_dir,
            'datas',
            'gunung-madu-dataset.csv'
        )
        output_file_path =  os.path.join(
            self.base_dir,
            'datas',
            'output-gunung-madu-dataset2.csv'
        )
        df = pd.read_csv(file_path)
        df.head()

        ## Define the stages
        # Fungsi untuk menentukan stage berdasarkan NDVI, CGDD, dan Yield
        def determine_stage(row):
            ndvi = row['avg_ndvi']
            cgdd = row['cgdd']
            yld = row['yield']

            # if ndvi < 5000 and cgdd < 500:
            #     return 'Germination'
            # elif 5000 <= ndvi < 7000 and cgdd < 1200:
            #     return 'Tillering'
            # elif ndvi >= 7000 and cgdd < 2200:
            #     return 'Grand Growth'
            # elif ndvi < 7000 and cgdd >= 2200:
            #     return 'Maturity'
            # elif yld > 0 and ndvi < 6000:
            #     return 'Harvest'
            # else:
            #     return 'Unknown'

            if yld > 0:
                return 'Harvest'
            elif ndvi < 4000:
                return 'Germination'
            elif 4000 <= ndvi < 6000:
                return 'Tillering'
            elif 6000 <= ndvi < 8000:
                return 'Grand Growth'
            elif ndvi >= 8000:
                return 'Maturity'
            else:
                return 'Unknown'

        # # Terapkan ke DataFrame
        df['stage'] = df.apply(determine_stage, axis=1)

        # Tampilkan beberapa hasil
        df[['month', 'year', 'avg_ndvi', 'cgdd', 'yield', 'stage']].head(12)

        df.to_csv(output_file_path, index=True)

