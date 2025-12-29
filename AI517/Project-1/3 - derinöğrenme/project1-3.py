import os
import numpy as np
try:
    import matplotlib.pyplot as plt
    import seaborn as sns
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    print("Uyarı: Matplotlib yüklü değil, grafikler oluşturulmayacak.")
from PIL import Image
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms, models
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
import time

print("=" * 80)
print("DERİN ÖĞRENME İLE GÖRÜNTÜ SINIFLANDIRMA PROJESİ (PYTORCH)")
print("=" * 80)

# Cihaz kontrolü (GPU varsa kullan)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"Kullanılan Cihaz: {device}")

# --- 1. VERİ SETİ BİLGİLERİ VE PARAMETRELER ---
print("\n" + "=" * 80)
print("1. VERİ SETİ BİLGİLERİ VE PARAMETRELER")
print("=" * 80)

data_dir = 'proje_veri_seti'
classes = ['1_filizlenme_donemi', '2_olgunlasma_donemi', '3_kis_uykusu_donemi']
class_names = ['Filizlenme Dönemi', 'Olgunlaşma Dönemi', 'Kış Uykusu Dönemi']

# Model Parametreleri
IMG_SIZE = 224
BATCH_SIZE = 16
EPOCHS = 5  # Kullanıcı isteği üzerine azaltıldı
LEARNING_RATE = 0.001

# Veri seti istatistikleri
total_images = 0
class_counts = {}
class_image_types = {}

for class_name in classes:
    class_path = os.path.join(data_dir, class_name)
    if os.path.exists(class_path):
        images = [f for f in os.listdir(class_path) 
                 if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        count = len(images)
        class_counts[class_name] = count
        total_images += count
        
        formats = {}
        for img in images:
            ext = os.path.splitext(img)[1].lower()
            formats[ext] = formats.get(ext, 0) + 1
        class_image_types[class_name] = formats

print(f"\nToplam Görüntü Sayısı: {total_images}")
print(f"Sınıf Bazında Dağılım:")
for i, (class_name, count) in enumerate(class_counts.items()):
    print(f"  {i+1}. {class_names[i]}: {count} görüntü")

# --- 2. VERİ YÜKLEME VE DATASET SINIFI ---
print("\n" + "=" * 80)
print("2. VERİ YÜKLEME VE HAZIRLAMA")
print("=" * 80)

class PlantDataset(Dataset):
    def __init__(self, image_paths, labels, transform=None):
        self.image_paths = image_paths
        self.labels = labels
        self.transform = transform
        
    def __len__(self):
        return len(self.image_paths)
    
    def __getitem__(self, idx):
        img_path = self.image_paths[idx]
        label = self.labels[idx]
        
        try:
            image = Image.open(img_path).convert('RGB')
            if self.transform:
                image = self.transform(image)
            return image, label
        except Exception as e:
            print(f"Hata: {img_path} yüklenemedi. {e}")
            # Hata durumunda rastgele bir tensör döndür (ideal çözüm değil ama eğitimi kırmaz)
            return torch.zeros((3, IMG_SIZE, IMG_SIZE)), label

# Görüntü yollarını ve etiketleri topla
all_image_paths = []
all_labels = []

for idx, class_name in enumerate(classes):
    class_path = os.path.join(data_dir, class_name)
    if os.path.exists(class_path):
        images = [f for f in os.listdir(class_path) 
                 if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
        for img in images:
            all_image_paths.append(os.path.join(class_path, img))
            all_labels.append(idx)

# Eğitim ve test setlerine ayır
X_train, X_test, y_train, y_test = train_test_split(
    all_image_paths, all_labels, test_size=0.2, random_state=42, stratify=all_labels
)

print(f"Eğitim Seti: {len(X_train)} görüntü")
print(f"Test Seti: {len(X_test)} görüntü")

# Transformasyonlar (Veri Artırma ve Normalizasyon)
train_transforms = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(20),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

test_transforms = transforms.Compose([
    transforms.Resize((IMG_SIZE, IMG_SIZE)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

# Dataset ve DataLoader oluşturma
train_dataset = PlantDataset(X_train, y_train, transform=train_transforms)
test_dataset = PlantDataset(X_test, y_test, transform=test_transforms)

train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE, shuffle=False)

# --- 3. MODELLERİN TANIMLANMASI ---
print("\n" + "=" * 80)
print("3. MODELLERİN TANIMLANMASI")
print("=" * 80)

# Model 1: Özel CNN Modeli
class CustomCNN(nn.Module):
    def __init__(self, num_classes):
        super(CustomCNN, self).__init__()
        self.features = nn.Sequential(
            nn.Conv2d(3, 32, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.BatchNorm2d(32),
            
            nn.Conv2d(32, 64, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.BatchNorm2d(64),
            
            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(),
            nn.MaxPool2d(kernel_size=2, stride=2),
            nn.BatchNorm2d(128),
        )
        self.classifier = nn.Sequential(
            nn.Flatten(),
            nn.Linear(128 * (IMG_SIZE // 8) * (IMG_SIZE // 8), 512),
            nn.ReLU(),
            nn.Dropout(0.5),
            nn.Linear(512, num_classes)
        )

    def forward(self, x):
        x = self.features(x)
        x = self.classifier(x)
        return x

# Model 2: VGG16 Transfer Learning
def create_vgg16_model(num_classes):
    model = models.vgg16(weights=models.VGG16_Weights.IMAGENET1K_V1)
    # Parametreleri dondur
    for param in model.features.parameters():
        param.requires_grad = False
    
    # Sınıflandırıcıyı değiştir
    num_features = model.classifier[6].in_features
    model.classifier[6] = nn.Linear(num_features, num_classes)
    return model

# Modelleri başlat
cnn_model = CustomCNN(num_classes=len(classes)).to(device)
vgg16_model = create_vgg16_model(num_classes=len(classes)).to(device)

print("CNN Modeli ve VGG16 Modeli oluşturuldu.")

# --- 4. EĞİTİM FONKSİYONLARI ---
def train_model(model, train_loader, test_loader, criterion, optimizer, num_epochs, model_name):
    print(f"\n{model_name} Eğitimi Başlıyor ({num_epochs} Epoch)...")
    start_time = time.time()
    history = {'train_accuracy': [], 'train_loss': [], 'val_accuracy': [], 'val_loss': []}
    
    for epoch in range(num_epochs):
        # Eğitim
        model.train()
        train_running_loss = 0.0
        train_correct = 0
        train_total = 0
        
        for inputs, labels in train_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            
            train_running_loss += loss.item() * inputs.size(0)
            _, predicted = torch.max(outputs, 1)
            train_total += labels.size(0)
            train_correct += (predicted == labels).sum().item()
        
        train_epoch_loss = train_running_loss / len(train_loader.dataset)
        train_epoch_acc = train_correct / train_total
        history['train_loss'].append(train_epoch_loss)
        history['train_accuracy'].append(train_epoch_acc)
        
        # Validation (Test seti üzerinde)
        model.eval()
        val_running_loss = 0.0
        val_correct = 0
        val_total = 0
        
        with torch.no_grad():
            for inputs, labels in test_loader:
                inputs, labels = inputs.to(device), labels.to(device)
                outputs = model(inputs)
                loss = criterion(outputs, labels)
                
                val_running_loss += loss.item() * inputs.size(0)
                _, predicted = torch.max(outputs, 1)
                val_total += labels.size(0)
                val_correct += (predicted == labels).sum().item()
        
        val_epoch_loss = val_running_loss / len(test_loader.dataset)
        val_epoch_acc = val_correct / val_total
        history['val_loss'].append(val_epoch_loss)
        history['val_accuracy'].append(val_epoch_acc)
        
        print(f"Epoch {epoch+1}/{num_epochs} - Train Loss: {train_epoch_loss:.4f} - Train Acc: {train_epoch_acc:.4f} - Val Loss: {val_epoch_loss:.4f} - Val Acc: {val_epoch_acc:.4f}")
        
    time_elapsed = time.time() - start_time
    print(f"{model_name} Eğitimi Tamamlandı. Süre: {time_elapsed:.0f}s")
    return history

def evaluate_model(model, test_loader):
    model.eval()
    all_preds = []
    all_labels = []
    
    with torch.no_grad():
        for inputs, labels in test_loader:
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)
            _, preds = torch.max(outputs, 1)
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
            
    return np.array(all_labels), np.array(all_preds)

# --- 5. MODELLERİN EĞİTİMİ ---
print("\n" + "=" * 80)
print("4. MODELLERİN EĞİTİMİ")
print("=" * 80)

criterion = nn.CrossEntropyLoss()

# CNN Eğitimi
optimizer_cnn = optim.Adam(cnn_model.parameters(), lr=LEARNING_RATE)
cnn_history = train_model(cnn_model, train_loader, test_loader, criterion, optimizer_cnn, EPOCHS, "Özel CNN")

# VGG16 Eğitimi
optimizer_vgg = optim.Adam(vgg16_model.classifier.parameters(), lr=LEARNING_RATE) # Sadece classifier eğitiliyor
vgg16_history = train_model(vgg16_model, train_loader, test_loader, criterion, optimizer_vgg, EPOCHS, "VGG16 Transfer Learning")

# --- 6. DEĞERLENDİRME VE SONUÇLAR ---
print("\n" + "=" * 80)
print("5. DEĞERLENDİRME VE SONUÇLAR")
print("=" * 80)

# CNN Değerlendirme
cnn_labels, cnn_preds = evaluate_model(cnn_model, test_loader)
print("\n--- Özel CNN Modeli Raporu ---")
print(classification_report(cnn_labels, cnn_preds, target_names=class_names))
cnn_acc = (cnn_labels == cnn_preds).mean()

# VGG16 Değerlendirme
vgg_labels, vgg_preds = evaluate_model(vgg16_model, test_loader)
print("\n--- VGG16 Transfer Learning Modeli Raporu ---")
print(classification_report(vgg_labels, vgg_preds, target_names=class_names))
vgg_acc = (vgg_labels == vgg_preds).mean()

# Karşılaştırma
print("\n" + "=" * 80)
print("SONUÇ KARŞILAŞTIRMASI")
print("=" * 80)
print(f"{'Model':<25} | {'Test Doğruluğu':<15}")
print("-" * 45)
print(f"{'Özel CNN':<25} | {cnn_acc:.4f}")
print(f"{'VGG16 Transfer Learning':<25} | {vgg_acc:.4f}")

if vgg_acc > cnn_acc:
    print(f"\nKazanan: VGG16 (Fark: {(vgg_acc - cnn_acc)*100:.2f}%)")
else:
    print(f"\nKazanan: Özel CNN (Fark: {(cnn_acc - vgg_acc)*100:.2f}%)")

# Grafiklerin Oluşturulması
print("\n" + "=" * 80)
print("GRAFİKLERİN OLUŞTURULMASI")
print("=" * 80)

if MATPLOTLIB_AVAILABLE:
    try:
        # Şekil 1: Eğitim Geçmişi Grafikleri
        fig, axes = plt.subplots(2, 2, figsize=(16, 12))
        
        # CNN Accuracy
        axes[0, 0].plot(range(1, EPOCHS+1), cnn_history['train_accuracy'], 'b-o', label='Eğitim Doğruluğu', linewidth=2, markersize=8)
        axes[0, 0].plot(range(1, EPOCHS+1), cnn_history['val_accuracy'], 'r-s', label='Test Doğruluğu', linewidth=2, markersize=8)
        axes[0, 0].set_title('Özel CNN Modeli - Doğruluk (Accuracy)', fontsize=14, fontweight='bold')
        axes[0, 0].set_xlabel('Epoch', fontsize=12)
        axes[0, 0].set_ylabel('Doğruluk', fontsize=12)
        axes[0, 0].legend(fontsize=11)
        axes[0, 0].grid(True, alpha=0.3)
        axes[0, 0].set_ylim([0, 1.1])
        
        # CNN Loss
        axes[0, 1].plot(range(1, EPOCHS+1), cnn_history['train_loss'], 'b-o', label='Eğitim Kaybı', linewidth=2, markersize=8)
        axes[0, 1].plot(range(1, EPOCHS+1), cnn_history['val_loss'], 'r-s', label='Test Kaybı', linewidth=2, markersize=8)
        axes[0, 1].set_title('Özel CNN Modeli - Kayıp (Loss)', fontsize=14, fontweight='bold')
        axes[0, 1].set_xlabel('Epoch', fontsize=12)
        axes[0, 1].set_ylabel('Kayıp', fontsize=12)
        axes[0, 1].legend(fontsize=11)
        axes[0, 1].grid(True, alpha=0.3)
        
        # VGG16 Accuracy
        axes[1, 0].plot(range(1, EPOCHS+1), vgg16_history['train_accuracy'], 'g-o', label='Eğitim Doğruluğu', linewidth=2, markersize=8)
        axes[1, 0].plot(range(1, EPOCHS+1), vgg16_history['val_accuracy'], 'm-s', label='Test Doğruluğu', linewidth=2, markersize=8)
        axes[1, 0].set_title('VGG16 Transfer Learning - Doğruluk (Accuracy)', fontsize=14, fontweight='bold')
        axes[1, 0].set_xlabel('Epoch', fontsize=12)
        axes[1, 0].set_ylabel('Doğruluk', fontsize=12)
        axes[1, 0].legend(fontsize=11)
        axes[1, 0].grid(True, alpha=0.3)
        axes[1, 0].set_ylim([0, 1.1])
        
        # VGG16 Loss
        axes[1, 1].plot(range(1, EPOCHS+1), vgg16_history['train_loss'], 'g-o', label='Eğitim Kaybı', linewidth=2, markersize=8)
        axes[1, 1].plot(range(1, EPOCHS+1), vgg16_history['val_loss'], 'm-s', label='Test Kaybı', linewidth=2, markersize=8)
        axes[1, 1].set_title('VGG16 Transfer Learning - Kayıp (Loss)', fontsize=14, fontweight='bold')
        axes[1, 1].set_xlabel('Epoch', fontsize=12)
        axes[1, 1].set_ylabel('Kayıp', fontsize=12)
        axes[1, 1].legend(fontsize=11)
        axes[1, 1].grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('egitim_gecmisi.png', dpi=300, bbox_inches='tight')
        print("✓ Şekil 1: Eğitim geçmişi grafikleri 'egitim_gecmisi.png' olarak kaydedildi")
        
        # Şekil 2: Confusion Matrix Grafikleri
        cm_cnn = confusion_matrix(cnn_labels, cnn_preds)
        cm_vgg = confusion_matrix(vgg_labels, vgg_preds)
        
        fig, axes = plt.subplots(1, 2, figsize=(16, 7))
        
        # CNN Confusion Matrix
        sns.heatmap(cm_cnn, annot=True, fmt='d', cmap='Blues', ax=axes[0], 
                   xticklabels=class_names, yticklabels=class_names,
                   cbar_kws={'label': 'Örnek Sayısı'}, linewidths=0.5, linecolor='gray')
        axes[0].set_title('Özel CNN Modeli - Hata Matrisi (Confusion Matrix)', fontsize=14, fontweight='bold')
        axes[0].set_ylabel('Gerçek Sınıf', fontsize=12)
        axes[0].set_xlabel('Tahmin Edilen Sınıf', fontsize=12)
        axes[0].tick_params(labelsize=10)
        
        # VGG16 Confusion Matrix
        sns.heatmap(cm_vgg, annot=True, fmt='d', cmap='Greens', ax=axes[1], 
                   xticklabels=class_names, yticklabels=class_names,
                   cbar_kws={'label': 'Örnek Sayısı'}, linewidths=0.5, linecolor='gray')
        axes[1].set_title('VGG16 Transfer Learning - Hata Matrisi (Confusion Matrix)', fontsize=14, fontweight='bold')
        axes[1].set_ylabel('Gerçek Sınıf', fontsize=12)
        axes[1].set_xlabel('Tahmin Edilen Sınıf', fontsize=12)
        axes[1].tick_params(labelsize=10)
        
        plt.tight_layout()
        plt.savefig('hata_matrisi.png', dpi=300, bbox_inches='tight')
        print("✓ Şekil 2: Hata matrisi grafikleri 'hata_matrisi.png' olarak kaydedildi")
        
    except Exception as e:
        print(f"\nGrafik oluşturulurken hata: {e}")
        import traceback
        traceback.print_exc()
else:
    print("Matplotlib yüklü olmadığı için grafikler oluşturulamadı.")
    print("Grafikleri oluşturmak için: pip install matplotlib seaborn")

print("\n" + "=" * 80)
print("PROJE TAMAMLANDI!")
print("=" * 80)
