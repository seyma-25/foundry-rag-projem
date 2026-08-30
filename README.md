# Yerel RAG Asistanım (Foundry Local)

Bu, Microsoft Foundry Local kullanarak tamamen **çevrimdışı** çalışan,
kendi belgelerinden soru cevaplayan bir RAG (Retrieval-Augmented
Generation) asistanı. Windows'ta çalışacak şekilde hazırlandı.

## 0) Ön koşullar

- Windows 10 (build 26100+) veya Windows 11
- Python 3.11 veya üzeri (`python --version` ile kontrol et)
- İnternet bağlantısı (sadece kurulum ve model indirme için gerekli —
  kurulumdan sonra tamamen offline çalışır)

## 1) Foundry Local'ı kur

PowerShell'i aç ve:

```powershell
winget install Microsoft.FoundryLocal
```

Kurulum bitince terminali kapatıp yeniden aç, sonra doğrula:

```powershell
foundry --version
```

## 2) Proje ortamını hazırla

Bu klasörü (foundry-rag-projem) bilgisayarına indirdikten sonra,
içine gir ve bir sanal ortam (virtual environment) oluştur — bu,
paketlerin diğer projelerinle karışmasını önler:

```powershell
cd foundry-rag-projem
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

> Not: `foundry-local-sdk-winml` paketi donanım hızlandırma
> (NPU/GPU) içerir ve Windows'ta önerilir. Kurulumda sorun
> yaşarsan `requirements.txt` içindeki satırı `foundry-local-sdk`
> ile değiştirip tekrar dene.

## 3) İlk çalıştırma (örnek belgeyle test)

`docs/` klasöründe seni test etmen için `ornek-belge.txt` adında
küçük bir örnek belge bıraktım (Foundry Local ve RAG hakkında).
Önce sistemin çalıştığını bu örnekle doğrula:

```powershell
python ingest.py
```

Bu komut:
1. Embedding modelini (qwen3-embedding-0.6b) indirir (ilk seferde
   biraz sürer, ~birkaç yüz MB).
2. `docs/` klasöründeki belgeleri parçalara böler.
3. Her parçayı vektöre (embedding) çevirir.
4. Hepsini `knowledge.db` adlı SQLite dosyasına kaydeder.

Sonra soru-cevap uygulamasını başlat:

```powershell
python app.py
```

İlk çalıştırmada sohbet modeli de (qwen2.5-0.5b, küçük ve hızlı bir
model) indirilecek. Sonra terminalde soru sorabilirsin, örneğin:

```
Soru: RAG nedir?
Soru: Foundry Local'ın GPU şartı var mı?
Soru: Fransa'nın başkenti neresi?   <-- bunu bilerek soruyoruz, çünkü
                                         belgede yok, asistanın "bu
                                         bilgi elimde yok" demesini
                                         bekliyoruz.
```

Çıkmak için `q` yaz.

## 4) Kendi belgelerini ekle (asıl proje burada başlıyor)

`docs/` klasörünü kendi `.txt` veya `.md` dosyalarınla değiştir/
doldur — ders notların, bir konudaki özetlerin, bir kılavuz, SSS
(FAQ) gibi ne istersen. Sonra:

```powershell
python ingest.py
python app.py
```

Her yeni belge eklediğinde veya değiştirdiğinde `ingest.py`'ı tekrar
çalıştırman yeterli (eski kayıtları silip yeniden oluşturur).

## Proje yapısı

```
foundry-rag-projem/
├── docs/            <- senin belgelerin (txt/md)
├── db.py            <- SQLite yardımcı fonksiyonları
├── ingest.py         <- belgeleri parçala + embed et + kaydet
├── app.py            <- soru-cevap döngüsü (retrieval + LLM)
├── requirements.txt
├── knowledge.db      <- ingest.py çalışınca otomatik oluşur
└── README.md
```

## Sırada ne var?

Bu, planındaki Faz 1-2'nin (RAG temelleri + çalışan prototip)
hızlandırılmış bir versiyonu. Çalıştırdıktan sonra sırasıyla şunları
birlikte derinleştirebiliriz:
- Chunk boyutu / overlap'in retrieval kalitesine etkisi
- `cosine_similarity` fonksiyonunun matematiği
- Farklı chat modelleri (phi-3.5-mini vb.) arasındaki hız/kalite dengesi
- Kaynak gösterme (citation) ve "bilmiyorum" davranışını test etme
- İsteğe bağlı: basit bir web arayüzü (Streamlit) eklemek
