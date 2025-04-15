
from flask import Flask, render_template, jsonify, request

app = Flask(__name__)
app.config.from_object("config")

from app.dashboard.helper import DashboardHelper
dashboard_helper = DashboardHelper()

@app.route('/')
def index():
    datas = {
        'avg_vi' : "---",
        'avg_wide': "---",
        'avg_yield': "---",
        'prediction_days': "---",
        'prediction_accuracy': "---",
    }
    return render_template('index.html', **datas)

@app.route('/calculate-data', methods=['GET'])
def get_image():
    req = request.args
    period = req.get("period")
    year = req.get("year")
    location = req.get("location")

    avg_ndvi = "No Data"
    result_avg_ndvi = dashboard_helper.calculate_ndvi(year=year, period=period, location=int(location))
    if (result_avg_ndvi):
        avg_ndvi = f"{result_avg_ndvi:.2f}"

    avg_wide = dashboard_helper.calculate_wide(location=int(location))

    time_year = int(year)
    if (period == "Q4"):
        time_year = int(year) + 1
    avg_yield = dashboard_helper.calculate_yield(year=time_year, hectare=avg_wide)


    days_remaining, confidence_score = "-", "-"
    if avg_ndvi != "No Data":
        result_days_remaining, result_confidence_score = dashboard_helper.calculate_harvest_day(result_avg_ndvi)
        days_remaining, confidence_score = f"{result_days_remaining:.0f}", f"{result_confidence_score:.0f}"+"%"
    
    datas = {
        'avg_vi' : avg_ndvi,
        'avg_wide': f"{avg_wide:.2f}" + " ha",
        'avg_yield': f"{avg_yield:.2f}" + " ton",
        'prediction_days': days_remaining,
        'prediction_accuracy': confidence_score
    }

    return jsonify({
        'status': True,
        'messages': 'Success get the data!',
        'datas': datas
    })

