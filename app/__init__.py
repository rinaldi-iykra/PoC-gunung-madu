
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)
app.config.from_object("config")

from app.dashboard.helper import DashboardHelper
dashboard_helper = DashboardHelper()

@app.route('/')
def index():
    datas = {
        'avg_vi' : 0.0,
        'avg_temp': 0,
        'avg_cgdd': 0.00,
        'avg_days': 0,
        'prediction_accuracy': 0
    }
    return render_template('index.html', **datas)

@app.route('/calculate-data', methods=['GET'])
def get_image():
    req = request.args
    period = req.get("period")
    year = req.get("year")

    avg_ndvi = "-"
    result_ndvi = dashboard_helper.calculate_ndvi(year=year, period=period)
    # result_ndvi = 0.56
    if (result_ndvi):
        avg_ndvi = "%.2f" % round(result_ndvi, 2)

    avg_temp = "-"
    result_avg_temp = dashboard_helper.calculate_temperature(year=year, period=period)
    # result_avg_temp = 30
    if (result_avg_temp):
        avg_temp = str(int(result_avg_temp))

    cgdd = dashboard_helper.calculate_cgdd(result_avg_temp)
    result_avg_days = dashboard_helper.calculate_prediction(result_ndvi, cgdd)
    
    datas = {
        'avg_vi' : avg_ndvi,
        'avg_temp': avg_temp,
        'avg_cgdd': cgdd,
        'avg_days': result_avg_days,
        'prediction_accuracy': 00
    }

    return jsonify({
        'status': True,
        'messages': 'Success get the data!',
        'datas': datas
    })

