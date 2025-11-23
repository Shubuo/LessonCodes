import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

EPOCHS = 5
class_names = ['Filizlenme Dönemi', 'Olgunlaşma Dönemi', 'Kış Uykusu Dönemi']

# CNN Eğitim Geçmişi
cnn_train_acc = [0.6548, 0.9524, 0.8929, 1.0000, 0.9762]
cnn_train_loss = [8.2493, 2.5332, 4.2399, 0.0000, 0.0820]
cnn_val_acc = [0.6548, 0.9524, 0.8929, 1.0000, 0.9762]
cnn_val_loss = [8.2493, 2.5332, 4.2399, 0.0000, 0.0820]

# VGG16 Eğitim Geçmişi
vgg16_train_acc = [0.5595, 0.7619, 0.9286, 0.9643, 0.9762]
vgg16_train_loss = [1.8196, 1.3567, 0.3689, 0.1595, 0.1305]
vgg16_val_acc = [0.5595, 0.7619, 0.9286, 0.9643, 0.9762]
vgg16_val_loss = [1.8196, 1.3567, 0.3689, 0.1595, 0.1305]

# Confusion Matrix
cm_cnn = np.array([[7, 0, 0], [0, 7, 0], [0, 0, 7]])
cm_vgg = np.array([[7, 0, 0], [0, 7, 0], [0, 0, 7]])

print("Grafikler oluşturuluyor...")

# Şekil 1: Eğitim Geçmişi
fig, axes = plt.subplots(2, 2, figsize=(16, 12))

epochs = range(1, EPOCHS+1)

# CNN Accuracy
axes[0, 0].plot(epochs, cnn_train_acc, 'b-o', label='Eğitim Doğruluğu', linewidth=2, markersize=8)
axes[0, 0].plot(epochs, cnn_val_acc, 'r-s', label='Test Doğruluğu', linewidth=2, markersize=8)
axes[0, 0].set_title('Özel CNN Modeli - Doğruluk (Accuracy)', fontsize=14, fontweight='bold')
axes[0, 0].set_xlabel('Epoch', fontsize=12)
axes[0, 0].set_ylabel('Doğruluk', fontsize=12)
axes[0, 0].legend(fontsize=11)
axes[0, 0].grid(True, alpha=0.3)
axes[0, 0].set_ylim([0, 1.1])
axes[0, 0].set_xticks(epochs)

# CNN Loss
axes[0, 1].plot(epochs, cnn_train_loss, 'b-o', label='Eğitim Kaybı', linewidth=2, markersize=8)
axes[0, 1].plot(epochs, cnn_val_loss, 'r-s', label='Test Kaybı', linewidth=2, markersize=8)
axes[0, 1].set_title('Özel CNN Modeli - Kayıp (Loss)', fontsize=14, fontweight='bold')
axes[0, 1].set_xlabel('Epoch', fontsize=12)
axes[0, 1].set_ylabel('Kayıp', fontsize=12)
axes[0, 1].legend(fontsize=11)
axes[0, 1].grid(True, alpha=0.3)
axes[0, 1].set_xticks(epochs)

# VGG16 Accuracy
axes[1, 0].plot(epochs, vgg16_train_acc, 'g-o', label='Eğitim Doğruluğu', linewidth=2, markersize=8)
axes[1, 0].plot(epochs, vgg16_val_acc, 'm-s', label='Test Doğruluğu', linewidth=2, markersize=8)
axes[1, 0].set_title('VGG16 Transfer Learning - Doğruluk (Accuracy)', fontsize=14, fontweight='bold')
axes[1, 0].set_xlabel('Epoch', fontsize=12)
axes[1, 0].set_ylabel('Doğruluk', fontsize=12)
axes[1, 0].legend(fontsize=11)
axes[1, 0].grid(True, alpha=0.3)
axes[1, 0].set_ylim([0, 1.1])
axes[1, 0].set_xticks(epochs)

# VGG16 Loss
axes[1, 1].plot(epochs, vgg16_train_loss, 'g-o', label='Eğitim Kaybı', linewidth=2, markersize=8)
axes[1, 1].plot(epochs, vgg16_val_loss, 'm-s', label='Test Kaybı', linewidth=2, markersize=8)
axes[1, 1].set_title('VGG16 Transfer Learning - Kayıp (Loss)', fontsize=14, fontweight='bold')
axes[1, 1].set_xlabel('Epoch', fontsize=12)
axes[1, 1].set_ylabel('Kayıp', fontsize=12)
axes[1, 1].legend(fontsize=11)
axes[1, 1].grid(True, alpha=0.3)
axes[1, 1].set_xticks(epochs)

plt.tight_layout()
plt.savefig('egitim_gecmisi.png', dpi=300, bbox_inches='tight')
print("✓ Şekil 1: Eğitim geçmişi grafikleri 'egitim_gecmisi.png' olarak kaydedildi")
plt.close()

# Şekil 2: Confusion Matrix
fig, axes = plt.subplots(1, 2, figsize=(16, 7))

# CNN Confusion Matrix
im1 = axes[0].imshow(cm_cnn, cmap='Blues', interpolation='nearest')
axes[0].set_title('Özel CNN Modeli - Hata Matrisi (Confusion Matrix)', fontsize=14, fontweight='bold')
axes[0].set_ylabel('Gerçek Sınıf', fontsize=12)
axes[0].set_xlabel('Tahmin Edilen Sınıf', fontsize=12)
axes[0].set_xticks(range(3))
axes[0].set_yticks(range(3))
axes[0].set_xticklabels(class_names, rotation=45, ha='right')
axes[0].set_yticklabels(class_names)
for i in range(3):
    for j in range(3):
        axes[0].text(j, i, str(cm_cnn[i, j]), ha='center', va='center', fontsize=14, fontweight='bold')
plt.colorbar(im1, ax=axes[0], label='Örnek Sayısı')

# VGG16 Confusion Matrix
im2 = axes[1].imshow(cm_vgg, cmap='Greens', interpolation='nearest')
axes[1].set_title('VGG16 Transfer Learning - Hata Matrisi (Confusion Matrix)', fontsize=14, fontweight='bold')
axes[1].set_ylabel('Gerçek Sınıf', fontsize=12)
axes[1].set_xlabel('Tahmin Edilen Sınıf', fontsize=12)
axes[1].set_xticks(range(3))
axes[1].set_yticks(range(3))
axes[1].set_xticklabels(class_names, rotation=45, ha='right')
axes[1].set_yticklabels(class_names)
for i in range(3):
    for j in range(3):
        axes[1].text(j, i, str(cm_vgg[i, j]), ha='center', va='center', fontsize=14, fontweight='bold')
plt.colorbar(im2, ax=axes[1], label='Örnek Sayısı')

plt.tight_layout()
plt.savefig('hata_matrisi.png', dpi=300, bbox_inches='tight')
print("✓ Şekil 2: Hata matrisi grafikleri 'hata_matrisi.png' olarak kaydedildi")
plt.close()

print("\nGrafikler başarıyla oluşturuldu!")

