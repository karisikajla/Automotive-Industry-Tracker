import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')))

import chromadb
from embeddings.embedder import get_model, build_document_text
from utils.logger import logging

CHROMA_PATH = os.path.abspath(os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data', 'embeddings', 'chroma_db'
))
COLLECTION_NAME = "data"

_client = None
_collection = None

def get_client():
    global _client
    if _client is None:
        os.makedirs(CHROMA_PATH, exist_ok=True)
        _client = chromadb.PersistentClient(path=CHROMA_PATH)
        logging.info(f"ChromaDB client connected at: {CHROMA_PATH}")
    return _client

def get_collection(reset=False):
    global _collection
    client = get_client()
    if reset:
        try:
            client.delete_collection(COLLECTION_NAME)
            logging.info(f"Deleted existing collection: {COLLECTION_NAME}")
        except Exception:
            pass
    _collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"}
    )
    logging.info(f"Collection '{COLLECTION_NAME}' ready. Count: {_collection.count()}")
    return _collection

def add_records(df, reset=False):
    collection = get_collection(reset=reset)
    model = get_model()

    existing_ids = set()
    if collection.count() > 0:
        existing = collection.get()
        existing_ids = set(existing["ids"])

    documents = []
    metadatas = []
    ids = []

    for idx, row in df.iterrows():
        record_id = str(idx)
        if record_id in existing_ids:
            continue

        doc_text = build_document_text(row.to_dict())
        if not doc_text.strip():
            continue

        make = str(row.get("data.make") or row.get("make", "Unknown"))
        model_name = str(row.get("data.model") or row.get("model", "Unknown"))
        year = row.get("data.year") or row.get("year", 0)
        source = str(row.get("source", "unknown"))

        try:
            year = int(float(year)) if year else 0
        except Exception:
            year = 0

        documents.append(doc_text)
        metadatas.append({
            "make": make,
            "model": model_name,
            "year": year,
            "source": source
        })
        ids.append(record_id)

    if not documents:
        logging.info("No new records to add to ChromaDB")
        return 0

    batch_size = 100
    for i in range(0, len(documents), batch_size):
        batch_docs = documents[i:i+batch_size]
        batch_embeddings = model.encode(batch_docs, normalize_embeddings=True).tolist()
        collection.add(
            documents=batch_docs,
            embeddings=batch_embeddings,
            metadatas=metadatas[i:i+batch_size],
            ids=ids[i:i+batch_size]
        )

    logging.info(f"Added {len(documents)} records to ChromaDB")
    return len(documents)

def query_collection(query_texts, n_results=5, where=None):
    collection = get_collection()
    model = get_model()

    if isinstance(query_texts, str):
        query_texts = [query_texts]

    query_embeddings = model.encode(query_texts, normalize_embeddings=True).tolist()

    kwargs = {"query_embeddings": query_embeddings, "n_results": n_results}
    if where:
        kwargs["where"] = where

    results = collection.query(**kwargs)
    return results

def get_collection_count():
    return get_collection().count()