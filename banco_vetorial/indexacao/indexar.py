# ── ETAPA 3: Indexação — ChromaDB (embeddings) + BM25 

import json
import pickle
from pathlib import Path

import chromadb
from chromadb.utils.embedding_functions import DefaultEmbeddingFunction
from rank_bm25 import BM25Okapi

# Caminhos
chunks_path = Path(__file__).parent.parent / "chunks" / "chunks.json"
data_path   = Path(__file__).parent.parent / "data"
bm25_path   = Path(__file__).parent / "bm25_index.pkl"

# Carrega os chunks
with open(chunks_path, "r", encoding="utf-8") as f:
    chunks = json.load(f)

print(f"Total de chunks: {len(chunks)}\n")

# ── ChromaDB 
client = chromadb.PersistentClient(path=str(data_path))

try:
    client.delete_collection("documentos")
    print("Coleção anterior removida.")
except Exception:
    pass

collection = client.create_collection(
    name="documentos",
    embedding_function=DefaultEmbeddingFunction(),
    metadata={"hnsw:space": "cosine"},
)

collection.add(
    ids=[c["id"] for c in chunks],
    documents=[c["text"] for c in chunks],
    metadatas=[{"source": c["source"]} for c in chunks],
)

print(f"ChromaDB: {collection.count()} chunks indexados\n")

# ── BM25 
textos    = [c["text"] for c in chunks]
ids       = [c["id"]   for c in chunks]
tokenized = [texto.lower().split() for texto in textos]

bm25 = BM25Okapi(tokenized)

with open(bm25_path, "wb") as f:
    pickle.dump({"bm25": bm25, "ids": ids, "texts": textos}, f)

print(f"BM25: índice salvo em {bm25_path}")
print("\nIndexação concluída!")
