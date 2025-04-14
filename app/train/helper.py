from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score, mean_squared_error
import numpy as np
import pandas as pd
import joblib

# # Assume you have a dataset 'data' with NDVI, CGDD, and harvest time
data = pd.DataFrame({
    'NDVI': [0.09, 0.46, 0.56],
    'CGDD': [23, 11.62, 12.36],
    'harvest_time': [240, 90, 150]
})

# # # Features (NDVI and CGDD) and Target (harvest time)
# X = data[['NDVI', 'CGDD']]
# # y = data['harvest_time']

# # # Train a Random Forest model
# # model = RandomForestRegressor()
# # model.fit(X, y)
# # joblib.dump(model, 'harvest_predictor.joblib')



# model = joblib.load('harvest_predictor.joblib')
# # Predict harvesting time from new NDVI + CGDD
# ndvi = 0.75
# cgdd = 8
# predicted_days = model.predict([[ndvi, cgdd]])
# print(predicted_days)
# print(f"Predicted harvesting time: {predicted_days[0]:.2f} days")




model = joblib.load('harvest_predictor.joblib')
# Test input features: NDVI, CGDD
X_test = np.array([
    [0.75, 300],       # Example test data (you can add more)
    [0.6, 300],
    [0.7, 200],
    [0.5, 170]
])

# Actual harvesting time in days (your ground truth)
y_true = np.array([105, 110, 100, 120])  # <-- adjust this based on real data
# Predict
y_pred = model.predict(X_test)
# Evaluation metrics
mse = mean_squared_error(y_true, y_pred)
r2 = r2_score(y_true, y_pred)
accuracy_percent = r2 * 100
print(f"Mean Squared Error: {mse:.2f}")
print(f"R² Score: {r2:.4f}")
print(f"Prediction Accuracy: {accuracy_percent:.2f}%")