# Veri seti ve Karar ağacının yüklenmesi 
from sklearn.datasets import load_iris
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
import matplotlib.pyplot as plt
from sklearn.model_selection import cross_val_score

from sklearn import cluster, datasets

# Zambak verisetinin yüklenmesi
iris = load_iris()
# X matrisine 4 sütun olarak 150 bitkinin özelliklerinin aktarılması 
X = iris.data
# y dizisine bu 150 bitkinin türlerinin (etiketlerinin) atanması 
y = iris.target
# Karar Ağacı Sınıflandırıcısının Modelinin Oluşturulması
# random_state = 0, sonuçların rastgele değişmemesi için
clf = DecisionTreeClassifier(random_state=0)

# Verinin %70'ini Eğitim, %30'unu test verisi olarak ayırıyoruz
X_train, X_test, y_train, y_test = train_test_split(X,y, train_size = 0.7, test_size = 
0.3, random_state = 0, stratify = y)

# Eğitim Verisi ile eğitimi gerçekleştiriyoruz
clf.fit(X_train,y_train)
test_sonuc = clf.predict(X_test)
#print(test_sonuc)
print('Karar ağaci doğruluk değeri: ' + str(accuracy_score(test_sonuc, y_test)))

print(cross_val_score(clf, iris.data, iris.target, cv=10))

cm = confusion_matrix(y_test, test_sonuc)
#print(cm)

# Show confusion matrix in a separate window
plt.matshow(cm)
plt.title('Confusion matrix')
plt.colorbar()
plt.ylabel('True label')
plt.xlabel('Predicted label')
plt.show()
