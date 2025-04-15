import joblib
import numpy as np

# Load model
model = joblib.load('ndvi_to_harvest_days.pkl')

# NDVI saat ini
# current_ndvi = 0.5553360086

current_ndvi = 0.6109580039
# current_ndvi = 0.5553360086
# current_ndvi = 0.287746753
# current_ndvi = 0.4322309277

# Ambil semua prediksi dari masing-masing tree
all_tree_preds = [tree.predict(np.array([[current_ndvi]]))[0] for tree in model.estimators_]

# Hitung nilai akhir sebagai rata-rata
days_remaining = np.mean(all_tree_preds)

# Hitung deviasi standar sebagai ukuran ketidakpastian
std_dev = np.std(all_tree_preds)

# Asumsi: makin kecil deviasi → makin tinggi confidence
# Konversi ke "confidence score" secara heuristik (semakin kecil deviasi, semakin tinggi confidence)
confidence_score = max(0, min(100, 100 - (std_dev / days_remaining * 100)))

# Output
print(f"🌾 Prediksi sisa hari menuju panen: {days_remaining:.0f} hari")
print(f"📈 Estimasi kepercayaan model: {confidence_score:.2f}% (deviasi: {std_dev:.2f} hari)")
