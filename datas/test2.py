import joblib
import numpy as np
import pandas as pd

# Load model dan polynomial transformer
model = joblib.load('yield_per_hectare_model.pkl')
poly = joblib.load('year_poly_transform.pkl')

# Input dari user
year = 2025
hectare = 1200  # dalam hektar

# Transform tahun ke polynomial features
year_poly = poly.transform([[year]])

# Prediksi yield per hektar
yield_per_hectare = model.predict(year_poly)[0]

# Hitung total yield
total_yield = yield_per_hectare * hectare

print(f"Tahun: {year}")
print(f"Hektar: {hectare}")
print(f"Prediksi yield per hektar: {yield_per_hectare:.2f} ton/hektar")
print(f"Prediksi total yield: {total_yield:.2f} ton")
