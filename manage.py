#!/usr/bin/env python
# coding: utf-8

from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from app import app

from app.bmkg.helper import ApiBMKGHelper
from app.ee.helper import ApiEEHelper
from app.dashboard.helper import DashboardHelper

migrate = Migrate(app)
manager = Manager(app)

# bmkg_helper = ApiBMKGHelper()
# ee_helper = ApiEEHelper()
# dashboard_helper = DashboardHelper()

# @manager
# def test_api():
#     code = '18.08.08.2008'
#     response = bmkg_helper.get_weather(code)

# @manager
# def test_ee_ndvi():
#     lat, lon = -7.303611702, 112.2186007
#     radius = int(23.72757634)
#     year = 2021
#     ee_helper.calcualte_ndvi_peak(
#         lat, lon,
#         radius=radius,
#         year=year
#     )

# @manager
# def test_ee_stage():
#     ee_helper.calculate_stage()

# @manager
# def test_kml():
#     result = dashboard_helper.load_ee('NDVI')
#     print(result, "RESULT")

# @manager
# def test_ndvi():
#     # result = dashboard_helper.calculate_ndvi()
#     result = dashboard_helper.calculate_temperature()
#     print(result, "RESULT")




if __name__ == '__main__':
    manager.run()