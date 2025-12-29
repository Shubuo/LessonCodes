import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression, Ridge, Lasso
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.preprocessing import StandardScaler

# --- 1. VERİ SETİ ÜRETİMİ (Gen AI Yaklaşımı) ---
print("=" * 80)
print("REKLAM HARCADIĞI BÜTÇE VE SATIŞ TAHMİNİ - SENTETİK VERİ SETİ")
print("=" * 80)

np.random.seed(42)
# 200 adet veri noktası
n_samples = 200
# Reklam bütçesi (X): 10 ile 100 birim arasında rastgele
X = np.random.uniform(10, 100, size=(n_samples, 1))
# Satış (y): Formül = 3 * X + 50 (Sabit) + Gürültü
# Gerçek hayatta ilişki tam doğrusal olmaz, sapmalar olur (Gürültü ekliyoruz)
noise = np.random.normal(0, 25, size=n_samples) 
y = 3 * X.ravel() + 50 + noise

# Veri setini DataFrame'e dönüştür ve CSV olarak kaydet
df_dataset = pd.DataFrame({
    'Reklam_Butcesi': X.ravel(),
    'Satis_Adedi': y
})

# CSV dosyasına kaydet
csv_filename = '../veri_setleri/reklam_satis_veri_seti.csv'
df_dataset.to_csv(csv_filename, index=False, encoding='utf-8')
print(f"\n✓ Veri seti '{csv_filename}' dosyasına kaydedildi.")

print(f"\nVeri Seti Oluşturuldu:")
print(f"- Toplam Örnek Sayısı: {n_samples}")
print(f"- Reklam Bütçesi Aralığı: {X.min():.1f} - {X.max():.1f}")
print(f"- Satış Aralığı: {y.min():.1f} - {y.max():.1f}")
print(f"- Gerçek İlişki: y = 3x + 50 + gürültü(σ=25)")
print(f"- CSV Dosyası: {csv_filename}")

# --- 2. EĞİTİM VE TEST AYRIMI ---
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
print(f"\nVeri Bölünmesi:")
print(f"- Eğitim Seti: {X_train.shape[0]} örnek")
print(f"- Test Seti: {X_test.shape[0]} örnek")

# SVR için veriyi normalize et (SVR ölçeklendirme gerektirir)
scaler = StandardScaler()
X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

# --- 3. REGRESYON MODELLERİNİN TANIMLANMASI VE EĞİTİMİ ---
print("\n" + "=" * 80)
print("REGRESYON MODELLERİNİN EĞİTİMİ")
print("=" * 80)

models = {
    'Linear Regression': LinearRegression(),
    'Ridge Regression (α=1.0)': Ridge(alpha=1.0, random_state=42),
    'Lasso Regression (α=1.0)': Lasso(alpha=1.0, random_state=42),
    'Random Forest (n=100)': RandomForestRegressor(n_estimators=100, random_state=42),
    'SVR (RBF Kernel)': SVR(kernel='rbf', C=100, gamma='scale')
}

results = {}

for name, model in models.items():
    print(f"\n{name} eğitiliyor...", end=" ")
    
    # SVR için normalize edilmiş veri kullan
    if name == 'SVR (RBF Kernel)':
        model.fit(X_train_scaled, y_train)
        y_pred = model.predict(X_test_scaled)
    else:
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
    
    # Metrikleri hesapla
    mse = mean_squared_error(y_test, y_pred)
    rmse = np.sqrt(mse)
    mae = mean_absolute_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)
    
    results[name] = {
        'MSE': mse,
        'RMSE': rmse,
        'MAE': mae,
        'R²': r2,
        'model': model,
        'predictions': y_pred
    }
    
    print("✓ Tamamlandı")

# --- 4. BAŞARI METRİKLERİNİN YAZDIRILMASI ---
print("\n" + "=" * 80)
print("BAŞARI METRİKLERİ KARŞILAŞTIRMASI")
print("=" * 80)

# Tablo başlığı
print(f"\n{'Yöntem':<30} | {'MSE':<12} | {'RMSE':<12} | {'MAE':<12} | {'R² Skoru':<12}")
print("-" * 80)

# Her model için sonuçları yazdır
for name, metrics in results.items():
    print(f"{name:<30} | {metrics['MSE']:<12.2f} | {metrics['RMSE']:<12.2f} | "
          f"{metrics['MAE']:<12.2f} | {metrics['R²']:<12.4f}")

# En iyi modeli bul
best_r2 = max(results.items(), key=lambda x: x[1]['R²'])
best_mse = min(results.items(), key=lambda x: x[1]['MSE'])

print("\n" + "=" * 80)
print("EN İYİ PERFORMANS")
print("=" * 80)
print(f"En Yüksek R² Skoru: {best_r2[0]} (R² = {best_r2[1]['R²']:.4f})")
print(f"En Düşük MSE: {best_mse[0]} (MSE = {best_mse[1]['MSE']:.2f})")

# --- 5. MODEL DENKLEMLERİ (Doğrusal modeller için) ---
print("\n" + "=" * 80)
print("DOĞRUSAL MODELLERİN DENKLEMLERİ")
print("=" * 80)

linear_models = ['Linear Regression', 'Ridge Regression (α=1.0)', 'Lasso Regression (α=1.0)']
for name in linear_models:
    if name in results:
        model = results[name]['model']
        if hasattr(model, 'coef_') and hasattr(model, 'intercept_'):
            print(f"{name}: y = {model.coef_[0]:.4f}x + {model.intercept_:.4f}")

# Gerçek ilişkiyi hatırlat
print(f"\nGerçek İlişki: y = 3.0000x + 50.0000 + gürültü")

# --- 6. ÖRNEK TAHMİNLER (En iyi model için) ---
print("\n" + "=" * 80)
print(f"ÖRNEK TAHMİNLER ({best_r2[0]})")
print("=" * 80)
print(f"{'Gerçek Reklam':<15} | {'Gerçek Satış':<15} | {'Tahmin':<15} | {'Hata':<15}")
print("-" * 80)

best_predictions = results[best_r2[0]]['predictions']
for i in range(min(10, len(X_test))):
    error = abs(y_test[i] - best_predictions[i])
    print(f"{X_test[i][0]:<15.2f} | {y_test[i]:<15.2f} | {best_predictions[i]:<15.2f} | {error:<15.2f}")

# --- 7. METRİK AÇIKLAMALARI ---
print("\n" + "=" * 80)
print("METRİK AÇIKLAMALARI")
print("=" * 80)
print("""
MSE (Mean Squared Error - Ortalama Karesel Hata):
  - Tahmin hatalarının karesinin ortalaması
  - Düşük değer daha iyi (0'a yakın ideal)
  - Büyük hataları daha fazla cezalandırır

RMSE (Root Mean Squared Error - Karekök Ortalama Karesel Hata):
  - MSE'nin karekökü
  - Orijinal birimlerle aynı ölçekte
  - Düşük değer daha iyi

MAE (Mean Absolute Error - Ortalama Mutlak Hata):
  - Tahmin hatalarının mutlak değerinin ortalaması
  - Düşük değer daha iyi
  - Tüm hataları eşit ağırlıkta değerlendirir

R² (R-squared - Belirlilik Katsayısı):
  - Modelin veriyi ne kadar iyi açıkladığını gösterir
  - 0 ile 1 arasında değişir (1 = mükemmel, 0 = kötü)
  - Negatif değerler modelin rastgele tahminden kötü olduğunu gösterir
""")

print("=" * 80)