"""
app.py
------
Sorgu (query) tarafı: kullanıcının sorusunu embed eder, knowledge.db
içindeki en alakalı parçaları bulur (retrieval), bunları bağlam
(context) olarak yerel LLM'e verir ve cevabı üretir (generation).

Bu üç adım -- Retrieve, Augment, Generate -- RAG'in kendisidir.

Kullanım:
    python app.py
(Önce ingest.py'ı çalıştırmış olman gerekir.)
"""

import numpy as np
from foundry_local_sdk import Configuration, FoundryLocalManager

import db

EMBEDDING_MODEL_ALIAS = "qwen3-embedding-0.6b"
# Hız için küçük bir model seçtik. Daha iyi cevap kalitesi istersen
# "phi-3.5-mini" dene (daha yavaş ama daha güçlü).
CHAT_MODEL_ALIAS = "qwen2.5-0.5b"

TOP_K = 3  # her soru için en alakalı kaç parça getirilecek

SYSTEM_PROMPT = """Sen, kullanıcının kendi belgelerinden oluşan bir bilgi \
tabanına dayanarak soru cevaplayan yerel bir asistansın.

Kurallar:
1. SADECE aşağıda sana verilen BAĞLAM (context) içindeki bilgiyi kullan.
   Kendi genel bilgini veya tahminini kullanma.
2. Cevabını hangi kaynak dosyadan aldığını belirt (örn: "kaynak.txt'ye göre...").
3. Eğer bağlamda soruyu cevaplayacak bilgi yoksa, uydurma -- açıkça
   "Bu bilgi elimdeki belgelerde yok." de.
4. Kısa, net ve Türkçe cevap ver.
"""


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-10))


def get_top_chunks(query_embedding: list[float], all_chunks: list[dict], k: int = TOP_K) -> list[dict]:
    """
    Basit brute-force benzerlik araması: sorunun embedding'ini,
    veritabanındaki her parçanın embedding'iyle kosinüs benzerliği
    (cosine similarity) ile karşılaştırır ve en yüksek k taneyi döndürür.

    Not: Bu yaklaşım küçük belge setleri için (onlarca-yüzlerce parça)
    gayet hızlı çalışır. Binlerce parçaya çıkarsan, özel bir vektör
    veritabanı (FAISS, Chroma vb.) düşünülebilir.
    """
    q = np.array(query_embedding)
    scored = []
    for chunk in all_chunks:
        sim = cosine_similarity(q, np.array(chunk["embedding"]))
        scored.append((sim, chunk))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [chunk for _, chunk in scored[:k]]


def build_prompt(question: str, chunks: list[dict]) -> list[dict]:
    context_parts = []
    for c in chunks:
        context_parts.append(f"[Kaynak: {c['source']}]\n{c['content']}")
    context = "\n\n---\n\n".join(context_parts)

    user_message = f"BAĞLAM:\n{context}\n\nSORU: {question}"

    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_message},
    ]


def main():
    if db.count_chunks() == 0:
        print("knowledge.db boş görünüyor. Önce 'python ingest.py' çalıştır.")
        return

    config = Configuration(app_name="foundry_rag_projem")
    FoundryLocalManager.initialize(config)
    manager = FoundryLocalManager.instance

    print(f"Embedding modeli yükleniyor: {EMBEDDING_MODEL_ALIAS}")
    embed_model = manager.catalog.get_model(EMBEDDING_MODEL_ALIAS)
    embed_model.download(lambda p: print(f"\r  %{p:.1f}", end="", flush=True))
    print()
    embed_model.load()
    embedding_client = embed_model.get_embedding_client()

    print(f"Sohbet modeli yükleniyor: {CHAT_MODEL_ALIAS}")
    chat_model = manager.catalog.get_model(CHAT_MODEL_ALIAS)
    chat_model.download(lambda p: print(f"\r  %{p:.1f}", end="", flush=True))
    print()
    chat_model.load()
    chat_client = chat_model.get_chat_client()

    all_chunks = db.get_all_chunks()
    print(f"\nHazır. Bilgi tabanında {len(all_chunks)} parça var.")
    print("Sorularını yaz, çıkmak için 'q' yaz.\n")

    while True:
        question = input("Soru: ").strip()
        if not question or question.lower() in ("q", "quit", "exit"):
            break

        # 1) Retrieve: soruyu embed et, en alakalı parçaları bul
        q_response = embedding_client.generate_embedding(question)
        q_embedding = q_response.data[0].embedding
        top_chunks = get_top_chunks(q_embedding, all_chunks)

        # 2) Augment: bulunan parçaları prompt'a ekle
        messages = build_prompt(question, top_chunks)

        # 3) Generate: yerel modelden cevabı akış (streaming) halinde al
        print("Cevap: ", end="", flush=True)
        for chunk in chat_client.complete_streaming_chat(messages):
            if chunk.choices and chunk.choices[0].delta and chunk.choices[0].delta.content:
                print(chunk.choices[0].delta.content, end="", flush=True)
        print("\n")

    embed_model.unload()
    chat_model.unload()


if __name__ == "__main__":
    main()
