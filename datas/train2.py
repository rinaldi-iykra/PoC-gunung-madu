import pandas as pd
import numpy as np
import joblib
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures

# Load data
df = pd.read_csv('dataset-yield.csv')

# Input: Year, Target: Yield/hectare
X = df[['Year']]
y = df['Yield/hectare']

# Buat polynomial features
poly = PolynomialFeatures(degree=3)
X_poly = poly.fit_transform(X)

# Train model
model = LinearRegression()
model.fit(X_poly, y)

# Simpan model dan transformer
joblib.dump(model, 'yield_per_hectare_model.pkl')
joblib.dump(poly, 'year_poly_transform.pkl')
