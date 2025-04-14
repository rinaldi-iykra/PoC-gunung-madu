from flask import Flask, render_template, jsonify, request
import ee
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials

app = Flask(__name__)

# Inisialisasi Google Earth Engine
def initialize_ee():
    credentials = ee.ServiceAccountCredentials(
        'iykra-online@iykra-online.iam.gserviceaccount.com',
        '/Users/rinaldi/Documents/IYKRA/PoC/gunung-madu/iykra-online-service-credential.json'
    )
    ee.Initialize(credentials)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get-image', methods=['GET'])
def get_image():
    # Ambil jenis citra yang diminta
    image_type = request.args.get('type', 'NDVI')
    print(image_type, "IMAGE TYPE")

    # Initialize Google Earth Engine
    initialize_ee()

    # Buat geometry area (polygon untuk area yang diinginkan)
    area = ee.Geometry.Polygon([
        [[105.2051646534618, -4.708865382035771],
         [105.2078225811218, -4.709224864499885],
         [105.2076585945317, -4.706996455914189],
         [105.2058363831134, -4.706309150550001],
         [105.2051646534618, -4.708865382035771]]
    ])

    # Pilih citra sesuai tipe
    if image_type == 'NDVI':
        image = ee.ImageCollection('COPERNICUS/S2') \
            .select(['B8', 'B4']) \
            .filterBounds(area) \
            .sort('system:time_start', False) \
            .first() \
            .normalizedDifference(['B8', 'B4']).rename('NDVI')
    elif image_type == 'NDWI':
        image = ee.ImageCollection('COPERNICUS/S2') \
            .select(['B8', 'B3']) \
            .filterBounds(area) \
            .sort('system:time_start', False) \
            .first() \
            .normalizedDifference(['B3', 'B8']).rename('NDWI')
    elif image_type == 'TEMP':
        image = ee.ImageCollection('COPERNICUS/S2') \
            .select(['B11']) \
            .filterBounds(area) \
            .sort('system:time_start', False) \
            .first()
    else:
        return jsonify({"error": f"Unknown image type: {image_type}"}), 400

    # Mendapatkan URL thumbnail citra
    url = image.getThumbURL({
        'min': -1,
        'max': 1,  # Adjust based on image value range
        'palette': ['blue', 'white', 'green'],  # Adjust palette for visualization
        'scale': 1000,  # Menurunkan resolusi gambar
        'dimensions': '512x512'  # Menyesuaikan ukuran thumbnail
    })

    return jsonify({'url': url})

if __name__ == '__main__':
    app.run(debug=True)
