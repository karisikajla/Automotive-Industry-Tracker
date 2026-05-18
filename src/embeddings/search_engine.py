import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')))

import pandas as pd
from embeddings.chroma_store import query_collection
from utils.logger import logging

def semantic_search(query, n_results=5, where=None):
    logging.info(f"Semantic search: '{query}'")
    results = query_collection([query], n_results=n_results, where=where)

    hits = []
    if results and results["documents"]:
        for i, doc in enumerate(results["documents"][0]):
            meta = results["metadatas"][0][i] if results["metadatas"] else {}
            distance = results["distances"][0][i] if results["distances"] else None
            score = round(1 - distance, 4) if distance is not None else None
            hits.append({
                "document": doc,
                "make": meta.get("make", ""),
                "model": meta.get("model", ""),
                "year": meta.get("year", ""),
                "source": meta.get("source", ""),
                "score": score
            })
    return hits

def keyword_search(query, df, columns=None, n_results=5):
    if columns is None:
        columns = ["data.make", "data.model", "data.component", "data.summary"]

    existing_cols = [c for c in columns if c in df.columns]
    if not existing_cols:
        return []

    query_lower = query.lower()
    mask = df[existing_cols].apply(
        lambda col: col.astype(str).str.lower().str.contains(query_lower, na=False)
    ).any(axis=1)

    matched = df[mask].head(n_results)
    results = []
    for _, row in matched.iterrows():
        results.append({
            "make": str(row.get("data.make") or row.get("make", "")),
            "model": str(row.get("data.model") or row.get("model", "")),
            "year": row.get("data.year") or row.get("year", ""),
            "source": str(row.get("source", ""))
        })
    return results

def compare_search(query, df, n_results=5):
    print(f"\n{'='*60}")
    print(f"Query: '{query}'")
    print(f"{'='*60}")

    print("\nSEMANTIC SEARCH")
    semantic = semantic_search(query, n_results=n_results)
    if semantic:
        for i, r in enumerate(semantic, 1):
            print(f"{i}. {r['make']} {r['model']} ({r['year']}) | score: {r['score']}")
    else:
        print("No results")

    print("\nKEYWORD SEARCH")
    keyword = keyword_search(query, df, n_results=n_results)
    if keyword:
        for i, r in enumerate(keyword, 1):
            print(f"{i}. {r['make']} {r['model']} ({r['year']})")
    else:
        print("No results")

    return {"semantic": semantic, "keyword": keyword}