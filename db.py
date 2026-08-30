"""
db.py
-----
SQLite yardımcı fonksiyonları.

Bu proje, doküman parçalarını (chunk) ve bunların embedding
vektörlerini tek bir SQLite dosyasında (knowledge.db) saklar.
SQLite tek dosyalık, sunucusuz bir veritabanıdır -- bu yüzden
kurulum derdi yoktur ve tüm veri tabanı tek bir dosyada taşınabilir.
"""

import sqlite3
import json
from pathlib import Path

DB_PATH = Path(__file__).parent / "knowledge.db"


def get_connection():
    """Veritabanı bağlantısı döndürür (yoksa dosyayı oluşturur)."""
    return sqlite3.connect(DB_PATH)


def init_db():
    """chunks tablosunu oluşturur (varsa dokunmaz)."""
    conn = get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS chunks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,       -- hangi dosyadan geldiği
            chunk_index INTEGER NOT NULL,
            content TEXT NOT NULL,      -- parçanın metni
            embedding TEXT NOT NULL     -- embedding vektörü, JSON string olarak
        )
        """
    )
    conn.commit()
    conn.close()


def clear_chunks():
    """Yeniden ingest yapılacaksa eski kayıtları temizler."""
    conn = get_connection()
    conn.execute("DELETE FROM chunks")
    conn.commit()
    conn.close()


def insert_chunk(source: str, chunk_index: int, content: str, embedding: list[float]):
    conn = get_connection()
    conn.execute(
        "INSERT INTO chunks (source, chunk_index, content, embedding) VALUES (?, ?, ?, ?)",
        (source, chunk_index, content, json.dumps(embedding)),
    )
    conn.commit()
    conn.close()


def get_all_chunks():
    """Tüm parçaları (embedding'leri Python listesine çevirerek) döndürür."""
    conn = get_connection()
    rows = conn.execute("SELECT id, source, chunk_index, content, embedding FROM chunks").fetchall()
    conn.close()

    result = []
    for row in rows:
        result.append(
            {
                "id": row[0],
                "source": row[1],
                "chunk_index": row[2],
                "content": row[3],
                "embedding": json.loads(row[4]),
            }
        )
    return result


def count_chunks() -> int:
    conn = get_connection()
    n = conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
    conn.close()
    return n
