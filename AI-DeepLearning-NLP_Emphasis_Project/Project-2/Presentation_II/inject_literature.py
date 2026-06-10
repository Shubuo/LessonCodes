import re

file_path = "/Users/buraky/1-CODE/personal/0-Lessons/NLP_Emphasis_Project/Project-2/Presentation_II/presentation-II.md"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Define the new slide
new_slide = """

---

# Literatür Taraması: Güncel Türkçe Yaklaşımlar

<div class="two-col">
<div>

## 4. BERTurk-contrastive (Dehghan & Amasyalı, 2025)
- **Odak Noktası:** Contrastive Learning (Karşıtlamalı Öğrenme) tekniğinin doğrudan Türkçe dil modellerine uyarlanması.
- **Katkısı:** Modelin uzayında anlamsal temsilleri daha homojen ayırarak vektör kalitesini artırır.
- **Projedeki Rolü:** Özel olarak entegre ettiğimiz `SCL` (Supervised Contrastive Learning) kaybının (loss) Türkçe metinlerdeki "Vurgulu/Vurgusuz" sınıf ayrımı konusundaki başarısını literatürde destekleyen en güncel referanstır.

</div>
<div>

## 5. BERT2D (Yılmaz vd., 2025)
- **Odak Noktası:** Kelime (word) ve alt-kelime (subword) ilişkilerini iki boyutlu bir yapıda modelleyen yeni nesil bir mimari.
- **Katkısı:** Sondan eklemeli dillerdeki (Türkçe gibi) tokenizasyon bilgi kaybını azaltmayı hedefler.
- **Projedeki Rolü:** Projede **pilot model** olarak entegre edilip test edilmiştir (Pilot Macro F1: 0.6191). Ancak `word_ids / subword_ids` hizalama (alignment) uyarıları nedeniyle ana model seçilmemiş, gelecek adımlar için güçlü bir alternatif olarak bırakılmıştır.

</div>
</div>"""

# Insert exactly before the "Uygulama: Kod Nasıl Çalışıyor?" section
target_header = "---"
next_section = "# Uygulama: Kod Nasıl Çalışıyor? (Custom Loss)"

search_pattern = f"{target_header}\n\n{next_section}"
replace_pattern = f"{new_slide}\n\n{target_header}\n\n{next_section}"

if search_pattern in content:
    new_content = content.replace(search_pattern, replace_pattern)
    with open(file_path, "w", encoding="utf-8") as f:
        f.write(new_content)
    print("Slide inserted successfully.")
else:
    print("Could not find the target location to insert the slide.")

