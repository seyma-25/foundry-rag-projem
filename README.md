# Yerel RAG Asistanım (Foundry Local)

Bu, Microsoft Foundry Local kullanarak tamamen **çevrimdışı** çalışan,
kendi yüklediğim belgeler ile soru cevaplayan bir RAG (Retrieval-Augmented
Generation) asistanı. Windows'ta çalışacak şekilde hazırladım.

## 1) Foundry Local'ı kurdum

PowerShell'i açtım ve:

```powershell
winget install Microsoft.FoundryLocal
```

Kurulum bitince terminali kapatıp yeniden açtım, sonra doğruladım:

```powershell
foundry --version
```

## 2) Proje ortamını hazırladım

```powershell
cd foundry-rag-projem
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

## 3) İlk çalıştırma ve test

Önce belgeleri işledim:

```powershell
python ingest.py
```

Bu komut ile:
1. Embedding modelini (qwen3-embedding-0.6b) indirdim.
2. `docs/` klasöründeki belgeleri parçalara böldüm.
3. Her parçayı vektöre (embedding) çevirdim.
4. Hepsini `knowledge.db` adlı SQLite dosyasına kaydettim.

Sonra soru-cevap uygulamasını başlattım:

```powershell
python app.py
```

İlk çalıştırmada sohbet modelini de (qwen2.5-0.5b) indiriyor, bu yüzden
biraz sürebilir. Doğru çalışıp çalışmadığını kontrol etmek için birkaç
soru sordum:
Soru: RAG nedir?
Soru: Foundry Local'ın GPU şartı var mı?
Soru: Fransa'nın başkenti neresi?


Son soruyu bilerek sordum çünkü belgelerimde bu bilgi yok — asistanın
"bu bilgi elimde yok" demesini bekliyorum, bu da halüsinasyon yapmadığını
kanıtlıyor.

Çıkmak için `q` yazdım.

## 4) Kendi belgelerimi ekledim

`docs/` klasörüne kendi belgelerimi ekledikten sonra:

```powershell
python ingest.py
python app.py
```

çalıştırdım. `ingest.py`'ı her yeni belge eklediğimde tekrar çalıştırıyorum
çünkü bu komut çalıştığında `docs/` klasöründeki TÜM belgeler (eski + yeni)
yeniden işlenir. Sonra aynı test sorularını tekrar sordum, ayrıca yeni
eklediğim belgelere özel sorular da denedim.
