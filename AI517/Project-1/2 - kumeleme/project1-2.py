import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.metrics import adjusted_rand_score, silhouette_score

# --- Veri Hazırlığı ---
try:
    # Acoustic Features.csv dosyasını yükle
    df = pd.read_csv('../veri_setleri/Acoustic Features.csv')
    
    # Class sütununu etiketler (y_true) olarak ayır
    y_true = df['Class'].values
    
    # Class sütunu dışındaki tüm sütunları özellikler (X) olarak al
    X = df.drop('Class', axis=1).values
    
    # Etiketleri sayısallaştırma (Başarı ölçümü için gerekli)
    le = LabelEncoder()
    y_true_encoded = le.fit_transform(y_true)
    
    # Normalizasyon (Kümeleme için çok kritiktir)
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    
    print(f"Veri Hazır: {X.shape[0]} örnek, {X.shape[1]} öznitelik.")
    
    # Hedeflenen küme sayısı (Veri setindeki gerçek sınıf sayısı)
    n_clusters = len(le.classes_)
    print(f"Tespit edilen sınıf sayısı: {n_clusters}")
    print(f"Sınıflar: {le.classes_}\n")

    # --- Yöntem 1: K-Means ---
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels_kmeans = kmeans.fit_predict(X_scaled)

    # --- Yöntem 2: Agglomerative Clustering ---
    agglo = AgglomerativeClustering(n_clusters=n_clusters, linkage='ward')
    labels_agglo = agglo.fit_predict(X_scaled)

    # --- Başarı Değerlendirmesi ---
    # 1. Adjusted Rand Index (ARI): Gerçek etiketlerle benzerliği ölçer (-1 ile 1 arası)
    ari_kmeans = adjusted_rand_score(y_true_encoded, labels_kmeans)
    ari_agglo = adjusted_rand_score(y_true_encoded, labels_agglo)
    
    # 2. Silhouette Score: Etiketlerden bağımsız küme kalitesini ölçer (-1 ile 1 arası)
    sil_kmeans = silhouette_score(X_scaled, labels_kmeans)
    sil_agglo = silhouette_score(X_scaled, labels_agglo)

    print("\n--- Sonuçların Karşılaştırılması ---")
    print(f"{'Yöntem':<25} | {'ARI (Gerçek Etiketle Uyum)':<30} | {'Silhouette (Küme Kalitesi)':<30}")
    print("-" * 85)
    print(f"{'K-Means':<25} | {ari_kmeans:<30.4f} | {sil_kmeans:<30.4f}")
    print(f"{'Agglomerative':<25} | {ari_agglo:<30.4f} | {sil_agglo:<30.4f}")

except Exception as e:
    print(f"Veri yükleme hatası: {e}")
    print("Lütfen ../veri_setleri/Acoustic Features.csv dosyasını kontrol ediniz.")