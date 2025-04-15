import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score

# Load data
df = pd.read_csv("dataset.csv")
df.columns = ['Sample', 'Quarter', 'Year', 'NDVI', 'Stage']

## Oversample
df_q1 = df[df['Quarter'] == 'Q1']
df_q2 = df[df['Quarter'] == 'Q2']
df_q3 = df[df['Quarter'] == 'Q3']
df_q4 = df[df['Quarter'] == 'Q4']

# Menentukan jumlah data yang dibutuhkan untuk oversampling
max_len = max(len(df_q1), len(df_q2), len(df_q3), len(df_q4))
print(max_len, "TOTAL DATA MAX")

df_q1_oversample = df_q1.sample(max_len, replace=True)
df_q2_oversample = df_q2.sample(max_len, replace=True)
df_q3_oversample = df_q3.sample(max_len, replace=True)
df_q4_oversample = df_q4.sample(max_len, replace=True)

df_balanced = pd.concat([df_q1_oversample, df_q2_oversample, df_q3_oversample, df_q4_oversample])

# Shuffle data jika diperlukan
df_balanced = df_balanced.sample(frac=1).reset_index(drop=True)

print(df_balanced)

# Mapping quarter ke hari ke-n (tengah kuartal)
quarter_to_day = {'Q1': 135, 'Q2': 45, 'Q3': 315, 'Q4': 270}
df_balanced['DayOfYear'] = df_balanced['Quarter'].map(quarter_to_day)

# Target kita: berapa hari lagi menuju panen dari posisi NDVI saat ini
# Panen terjadi pada hari ke-270 (Q3)
df_balanced['DaysToHarvest'] = 270 - df_balanced['DayOfYear']

# Buang data setelah panen (Q3 ke atas)
df_balanced = df_balanced[df_balanced['DayOfYear'] < 270]

# Buang baris dengan missing
df_balanced = df_balanced.dropna(subset=['NDVI', 'DaysToHarvest'])

# Fitur dan label
X = df_balanced[['NDVI']]
y = df_balanced['DaysToHarvest']

# Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=50)

# Train model
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate
y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)
r2 = r2_score(y_test, y_pred)

print("=== Model Evaluation ===")
print(f"Mean Absolute Error (MAE): {mae:.2f} days")
print(f"R² Score: {r2:.4f}")

# Simpan model
import joblib
joblib.dump(model, 'ndvi_to_harvest_days.pkl')
print("✅ Model saved as ndvi_to_harvest_days.pkl")
