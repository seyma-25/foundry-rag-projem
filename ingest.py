"""
ingest.py
---------
docs/ klasöründeki metin dosyalarını okur, parçalara (chunk) böler,
Foundry Local'ın embedding modeliyle her parçayı vektöre çevirir ve
SQLite veritabanına (knowledge.db) kaydeder.

Kullanım:
    python ingest.py
"""

from pathlib import Path
from foundry_local_sdk import Configuration, FoundryLocalManager

import db

DOCS_DIR = Path(__file__).parent / "docs"
EMBEDDING_MODEL_ALIAS = "qwen3-embedding-0.6b"

# Bir "chunk" kaç kelimeden oluşsun? RAG'de genelde 1-3 paragraf iyi çalışır.
CHUNK_SIZE_WORDS = 220
CHUNK_OVERLAP_WORDS = 40


def chunk_text(text: str, size: int = CHUNK_SIZE_WORDS, overlap: int = CHUNK_OVERLAP_WORDS) -> list[str]:
    """
    Metni kelime bazlı, örtüşmeli (overlap) parçalara böler.
    Örtüşme, bir cümlenin tam ortasından kesilip anlam kaybı
    yaşanmasını azaltır -- bir parçanın sonu, bir sonraki parçanın
    başıyla biraz çakışır.
    """
    words = text.split()
    if not words:
        return []

    chunks = []
    start = 0
    while start < len(words):
        end = start + size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        if end >= len(words):
            break
        start = end - overlap
    return chunks


def load_documents() -> dict[str, str]:
    """docs/ klasöründeki .txt ve .md dosyalarını okur."""
    documents = {}
    if not DOCS_DIR.exists():
        print(f"UYARI: {DOCS_DIR} klasörü yok, oluşturuluyor.")
        DOCS_DIR.mkdir(parents=True, exist_ok=True)

    for path in sorted(DOCS_DIR.glob("*")):
        if path.suffix.lower() in (".txt", ".md"):
            documents[path.name] = path.read_text(encoding="utf-8")

    return documents


def main():
    documents = load_documents()
    if not documents:
        print(f"'{DOCS_DIR}' klasöründe .txt veya .md dosyası bulunamadı.")
        print("Önce kendi belgelerini bu klasöre koy, sonra tekrar çalıştır.")
        return

    print(f"{len(documents)} belge bulundu: {list(documents.keys())}")

    # 1) Foundry Local'ı başlat
    config = Configuration(app_name="foundry_rag_projem")
    FoundryLocalManager.initialize(config)
    manager = FoundryLocalManager.instance

    # 2) Embedding modelini indir ve yükle
    print(f"\nEmbedding modeli indiriliyor/yükleniyor: {EMBEDDING_MODEL_ALIAS}")
    model = manager.catalog.get_model(EMBEDDING_MODEL_ALIAS)
    model.download(
        lambda p: print(f"\r  İndiriliyor: %{p:.1f}", end="", flush=True)
    )
    print()
    model.load()
    print("Embedding modeli hazır.")

    embedding_client = model.get_embedding_client()

    # 3) Veritabanını hazırla (baştan çalıştırıyorsak eski kayıtları temizle)
    db.init_db()
    db.clear_chunks()

    # 4) Her belgeyi parçala, embed et, kaydet
    total_chunks = 0
    for filename, text in documents.items():
        pieces = chunk_text(text)
        print(f"\n{filename}: {len(pieces)} parçaya bölündü.")

        for i, piece in enumerate(pieces):
            response = embedding_client.generate_embedding(piece)
            embedding = response.data[0].embedding
            db.insert_chunk(source=filename, chunk_index=i, content=piece, embedding=embedding)
            total_chunks += 1

    model.unload()

    print(f"\nBitti. Toplam {total_chunks} parça, {db.count_chunks()} kayıt olarak "
          f"knowledge.db dosyasına yazıldı.")


if __name__ == "__main__":
    main()
