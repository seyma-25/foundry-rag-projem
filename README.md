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
