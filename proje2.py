import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import os

# 2. CSV dosyasını oku
csv_path = "dosya yolu "   
df = pd.read_csv(csv_path)

# 3. Veri setinin ilk 10 satırına bakalım
print("Verinin ilk 10 satırı:")
print(df.head(10))

# 4. Veri yapısı hakkında genel bilgi (sütun adları, tipleri, eksik sayısı)
print("\nVeri seti bilgisi:")
df.info()

# 5. Sütun başlıklarını listeleyelim
print("\nSütun başlıkları:")
print(list(df.columns))

# 6. Eksik değerleri sütun bazında sayalım
print("\nEksik değer sayısı (sütun bazında):")
print(df.isnull().sum().sort_values(ascending=False))

# 7. Kopya satır var mı kontrol edelim
print("\nKopya satır sayısı:", df.duplicated().sum())

# 8. Veri setini temizleme için bir kopya oluşturalım
df_clean = df.copy()

# 9. Sütun isimlerini düzenleyelim (küçük harfe çevir, boşlukları '_' yap)
df_clean.columns = [c.strip().lower().replace(' ', '_') for c in df_clean.columns]
print("\nDüzenlenmiş sütun isimleri:")
print(list(df_clean.columns))

# 10. Yardımcı fonksiyon: sayısal değerleri güvenli şekilde dönüştürmek için
def safe_numeric(series):
    """
    Bir pandas serisini güvenli şekilde sayısal değerlere dönüştürür.
    Virgül, nokta gibi karakterleri temizler.
    """
    return pd.to_numeric(
        series.astype(str)
              .str.replace(',', '')
              .str.extract(r'([0-9\.]+)')[0],
        errors='coerce'
    )

# 11. 'rating' sütunu varsa sayısala çevir
if 'rating' in df_clean.columns:
    df_clean['rating'] = safe_numeric(df_clean['rating'])

# 12. Süre bilgisi (runtime, duration veya time) sütunu varsa dakika olarak çıkar
for col in ['duration', 'runtime', 'time']:
    if col in df_clean.columns:
        df_clean['duration_min'] = safe_numeric(df_clean[col])
        break  # ilk bulduğu sütunu kullanır

# 13. Yıl bilgisini sayısala çevirelim
if 'year' in df_clean.columns:
    df_clean['year'] = pd.to_numeric(df_clean['year'], errors='coerce').astype('Int64')

# 14. Oy sayısı (votes) sütununu sayısala çevirelim
if 'votes' in df_clean.columns:
    df_clean['votes'] = safe_numeric(df_clean['votes']).astype('Int64')

# 15. Tür bilgisini liste haline getirelim (virgül veya | ile ayrılmış olabilir)
if 'genres' in df_clean.columns:
    df_clean['genres_list'] = df_clean['genres'].astype(str).replace('nan', '').str.split(r'[,\|;]')
elif 'genre' in df_clean.columns:
    df_clean['genres_list'] = df_clean['genre'].astype(str).replace('nan', '').str.split(r'[,\|;]')
else:
    df_clean['genres_list'] = np.nan

# 16. Yönetmen bilgisini temizleyelim
if 'director' in df_clean.columns:
    df_clean['director'] = df_clean['director'].astype(str).replace('nan', '').str.strip()

# 17. Film adından parantez içindeki yılı çıkarıp sade bir başlık oluşturalım
if 'title' in df_clean.columns:
    df_clean['title_clean'] = (
        df_clean['title']
        .astype(str)
        .str.replace(r'\s*\(\d{4}\)\s*$', '', regex=True)
        .str.strip()
    )

# 18. Başlık + yıl bilgisine göre kopya satırları kaldıralım
if 'title_clean' in df_clean.columns and 'year' in df_clean.columns:
    before = len(df_clean)
    df_clean = df_clean.drop_duplicates(subset=['title_clean', 'year'])
    after = len(df_clean)
    print(f"\nKopyalar silindi: {before - after} satır.")

# 19. Temizlenen veri setinin genel durumuna bakalım
print("\nTemizlenmiş veri setinin boyutu:", df_clean.shape)
print("\nTemizlenmiş veri seti ilk 5 satır:")
print(df_clean.head())

# AŞAMA 2: KEŞİFSEL VERİ ANALİZİ (PANDAS & NUMPY)

# 1. Sayısal sütunları otomatik tespit edelim
numeric_cols = df_clean.select_dtypes(include=['int64', 'float64', 'Int64']).columns.tolist()
print("Sayılsal sütunlar:", numeric_cols)

# 2. Sayısal sütunlara genel bakış (temel istatistikler)
print("\nSayısal sütunların özet istatistikleri:")
print(df_clean[numeric_cols].describe())

# 3. IMDb puanı (imdbRating veya rating) sütununa göre en yüksek 20 filmi listeleyelim
# (veride imdbRating varsa onu kullan, yoksa rating)
rating_col = None
for c in ['imdbrating', 'rating']:
    if c in df_clean.columns:
        rating_col = c
        break

if rating_col:
    print(f"\nEn yüksek puanlı 20 film ({rating_col}):")
    top20 = df_clean.sort_values(by=rating_col, ascending=False).head(20)
    print(top20[['title_clean', 'year', rating_col]].head(20))
else:
    print("⚠️ Puan sütunu bulunamadı (imdbrating veya rating).")

# 4. En çok oylanan 20 filmi bulalım (imdbVotes veya votes sütunu varsa)
votes_col = None
for c in ['imdbvotes', 'votes']:
    if c in df_clean.columns:
        votes_col = c
        break

if votes_col:
    print(f"\nEn çok oylanan 20 film ({votes_col}):")
    top_voted = df_clean.sort_values(by=votes_col, ascending=False).head(20)
    print(top_voted[['title_clean', 'year', votes_col]].head(20))
else:
    print("⚠️ Oy sayısı sütunu bulunamadı (imdbvotes veya votes).")

# 5. Tür (genre) sütunundan türlerin dağılımını hesaplayalım
if 'genres_list' in df_clean.columns:
    # Liste sütununu tekil satırlara dönüştürüp say
    genre_counts = (
        df_clean['genres_list']
        .explode()
        .value_counts()
        .dropna()
    )
    print("\nEn yaygın türler:")
    print(genre_counts.head(10))
else:
    print("⚠️ Tür bilgisi (genres_list) bulunamadı.")

# 6. Yönetmen başına film sayısı ve ortalama puan hesaplayalım
if 'director' in df_clean.columns and rating_col:
    director_stats = (
        df_clean.groupby('director')
        .agg(film_sayisi=('title_clean', 'count'),
             ortalama_puan=(rating_col, 'mean'))
        .sort_values(by='film_sayisi', ascending=False)
    )
    print("\nEn çok film yöneten 10 yönetmen:")
    print(director_stats.head(10))
else:
    print("⚠️ Yönetmen veya puan sütunu bulunamadı.")

# 7. Süre (dakika) ile puan arasındaki korelasyonu hesaplayalım
if 'duration_min' in df_clean.columns and rating_col:
    corr = df_clean['duration_min'].corr(df_clean[rating_col])
    print(f"\nSüre (dakika) ile Puan ({rating_col}) arasındaki Pearson korelasyonu: {corr:.3f}")
else:
    print("⚠️ Süre (duration_min) veya puan sütunu eksik, korelasyon hesaplanamadı.")

# 8. Yıllara göre film sayısı (trend) incelemesi
if 'year' in df_clean.columns:
    year_trend = df_clean['year'].value_counts().sort_index()
    print("\nYıllara göre film sayısı:")
    print(year_trend.tail(15))  # son 15 yılı göster
else:
    print("⚠️ Yıl sütunu bulunamadı.")


    # AŞAMA 3: VERİ GÖRSELLEŞTİRME (MATPLOTLIB)

    # 1. Çıktı klasörü oluştur (Visual Studio Code projesinde)
output_dir = "outputs"
os.makedirs(output_dir, exist_ok=True)

# 2. Rating (puan) sütununu belirle
rating_col = None
for c in ['imdbrating', 'rating']:
    if c in df_clean.columns:
        rating_col = c
        break

# --------------------------------------------------------
# 3. Rating histogramı
# --------------------------------------------------------
if rating_col:
    plt.figure(figsize=(8, 5))
    plt.hist(df_clean[rating_col].dropna(), bins=20, edgecolor='black')
    plt.title("IMDb Puan Dağılımı")
    plt.xlabel("Puan")
    plt.ylabel("Film Sayısı")
    plt.grid(axis='y', linestyle='--', alpha=0.6)
    plt.tight_layout()

    # Görseli kaydet
    plt.savefig(os.path.join(output_dir, "rating_histogram.png"))
    plt.close()
    print("✅ rating_histogram.png kaydedildi.")
else:
    print("⚠️ Rating sütunu bulunamadı, histogram çizilemedi.")

# --------------------------------------------------------
# 4. En popüler türlerin (genre) bar grafiği
# --------------------------------------------------------
if 'genres_list' in df_clean.columns:
    genre_counts = df_clean['genres_list'].explode().value_counts().dropna().head(10)
    plt.figure(figsize=(8, 5))
    genre_counts.sort_values().plot(kind='barh')
    plt.title("En Popüler Film Türleri")
    plt.xlabel("Film Sayısı")
    plt.ylabel("Tür")
    plt.tight_layout()

    plt.savefig(os.path.join(output_dir, "top_genres_barh.png"))
    plt.close()
    print("✅ top_genres_barh.png kaydedildi.")
else:
    print("⚠️ Tür bilgisi (genres_list) yok, grafik çizilemedi.")

# --------------------------------------------------------
# 5. Süre (dakika) ile puan arasındaki ilişki (Scatter Plot)
# --------------------------------------------------------
if 'duration_min' in df_clean.columns and rating_col:
    plt.figure(figsize=(7, 5))
    plt.scatter(df_clean['duration_min'], df_clean[rating_col], alpha=0.4)
    plt.title("Film Süresi ile IMDb Puanı Arasındaki İlişki")
    plt.xlabel("Süre (dakika)")
    plt.ylabel("IMDb Puanı")
    plt.tight_layout()

    plt.savefig(os.path.join(output_dir, "duration_vs_rating_scatter.png"))
    plt.close()
    print("✅ duration_vs_rating_scatter.png kaydedildi.")
else:
    print("⚠️ Süre veya rating sütunu eksik, scatter çizilemedi.")

# --------------------------------------------------------
# 6. En popüler 6 tür için Boxplot (puan dağılımı)
# --------------------------------------------------------
if 'genres_list' in df_clean.columns and rating_col:
    top_genres = df_clean['genres_list'].explode().value_counts().index[:6]
    data_to_plot = []

    for genre in top_genres:
        mask = df_clean['genres_list'].apply(lambda lst: isinstance(lst, list) and genre in lst)
        data_to_plot.append(df_clean.loc[mask, rating_col].dropna())

    plt.figure(figsize=(9, 6))
    plt.boxplot(data_to_plot, labels=top_genres, patch_artist=True)
    plt.title("En Popüler Türlerde IMDb Puan Dağılımı")
    plt.xlabel("Tür")
    plt.ylabel("IMDb Puanı")
    plt.tight_layout()

    plt.savefig(os.path.join(output_dir, "rating_boxplot_top6genres.png"))
    plt.close()
    print("✅ rating_boxplot_top6genres.png kaydedildi.")
else:
    print("⚠️ Tür bilgisi yok, boxplot oluşturulamadı.")

# --------------------------------------------------------
# 7. Çizimler tamamlandığında mesaj verelim
# --------------------------------------------------------
print("\n🎉 Görseller başarıyla oluşturuldu!")
print(f"Tüm görseller '{output_dir}/' klasörüne kaydedildi.")

# AŞAMA 4: RAPORLAMA

# 1️⃣  Rapor klasörünü oluştur
report_dir = "Report"
os.makedirs(report_dir, exist_ok=True)

# 2️⃣  Dosya yolu belirle
report_path = os.path.join(report_dir, "imdb_raporu.txt")

# 3️⃣  Rating sütununu belirle
rating_col = None
for c in ['imdbrating', 'rating']:
    if c in df_clean.columns:
        rating_col = c
        break

# 4️⃣  Raporu derle
lines = []
lines.append("="*70)
lines.append("🎬 IMDb FİLM VERİ SETİ ANALİZİ RAPORU")
lines.append("="*70 + "\n")

# 📌 Genel Bilgiler
lines.append("📌 GENEL BİLGİLER")
lines.append(f"- Toplam film sayısı: {len(df_clean):,}")

if 'year' in df_clean.columns:
    lines.append(f"- Yıl aralığı: {int(df_clean['year'].min())} – {int(df_clean['year'].max())}")

if rating_col:
    ort = df_clean[rating_col].mean()
    med = df_clean[rating_col].median()
    lines.append(f"- Ortalama IMDb puanı: {ort:.2f}")
    lines.append(f"- Medyan IMDb puanı: {med:.2f}")

if 'duration_min' in df_clean.columns and rating_col:
    corr = df_clean['duration_min'].corr(df_clean[rating_col])
    lines.append(f"- Süre (dakika) ile puan arasındaki korelasyon: {corr:.3f}")

# 🎭 Tür analizi
if 'genres_list' in df_clean.columns:
    genre_counts = df_clean['genres_list'].explode().value_counts().dropna().head(10)
    lines.append("\n🎭 EN POPÜLER TÜRLER")
    for genre, count in genre_counts.items():
        lines.append(f"  • {genre:<15} : {count} film")

# 🌟 En yüksek puanlı 10 film
if rating_col:
    top10 = (
        df_clean[['title_clean', 'year', rating_col]]
        .sort_values(by=rating_col, ascending=False)
        .head(10)
        .reset_index(drop=True)
    )
    lines.append("\n🌟 EN YÜKSEK PUANLI 10 FİLM")
    for i, row in top10.iterrows():
        lines.append(f"  {i+1:2d}. {row['title_clean']} ({int(row['year'])}) — {row[rating_col]:.1f}")

# 🎬 En çok film çeken yönetmenler
if 'director' in df_clean.columns and rating_col:
    director_stats = (
        df_clean.groupby('director')
        .agg(film_sayisi=('title_clean', 'count'),
             ortalama_puan=(rating_col, 'mean'))
        .sort_values(by='film_sayisi', ascending=False)
        .head(10)
    )
    lines.append("\n🎬 EN ÇOK FİLM ÇEKEN YÖNETMENLER")
    for name, row in director_stats.iterrows():
        lines.append(f"  • {name:<25} : {row['film_sayisi']} film, ort. puan {row['ortalama_puan']:.2f}")

# 📈 Yıllara göre trend
if 'year' in df_clean.columns:
    year_counts = df_clean['year'].value_counts().sort_index()
    lines.append("\n📈 SON 10 YILDA ÇEKİLEN FİLM SAYISI")
    for year, count in year_counts.tail(10).items():
        lines.append(f"  {int(year)} : {count} film")

lines.append("\n" + "="*70)
lines.append("🧠 RAPOR SONU — Bu özet, veri setinin genel eğilimlerini gösterir.")
lines.append("="*70)

# 5️⃣  Raporu .txt dosyasına yaz
with open(report_path, "w", encoding="utf-8") as f:
    f.write("\n".join(lines))

# 6️⃣  Kullanıcıya bilgi ver
print("✅ Rapor başarıyla oluşturuldu!")
print(f"📁 Kaydedilen dosya: {report_path}")
print("\nİçeriği görmek için VS Code'da 'Report/imdb_raporu.txt' dosyasını açabilirsin.")

