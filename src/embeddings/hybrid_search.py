import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')))

from embeddings.search_engine import semantic_search, keyword_search
from utils.logger import logging

def reciprocal_rank_fusion(ranked_lists, k=60):
    scores = {}
    for ranked_list in ranked_lists:
        for rank, item in enumerate(ranked_list):
            key = item.get("make", "") + "_" + item.get("model", "") + "_" + str(item.get("year", ""))
            if key not in scores:
                scores[key] = {"item": item, "rrf_score": 0.0}
            scores[key]["rrf_score"] += 1.0 / (k + rank + 1)

    sorted_results = sorted(scores.values(), key=lambda x: x["rrf_score"], reverse=True)
    return [{"rrf_score": round(r["rrf_score"], 6), **r["item"]} for r in sorted_results]

def hybrid_search(query, df, n_results=10, k=60):
    logging.info(f"Hybrid search: '{query}'")

    semantic = semantic_search(query, n_results=n_results)
    keyword = keyword_search(query, df, n_results=n_results)

    combined = reciprocal_rank_fusion([semantic, keyword], k=k)
    return combined[:n_results]