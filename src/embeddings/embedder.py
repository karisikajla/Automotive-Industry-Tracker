import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..')))

from sentence_transformers import SentenceTransformer, util
import numpy as np
from utils.logger import logging

MODEL_NAME = "all-MiniLM-L6-v2"
_model = None

def get_model():
    global _model
    if _model is None:
        logging.info(f"Loading sentence-transformer model: {MODEL_NAME}")
        _model = SentenceTransformer(MODEL_NAME)
        logging.info("Model loaded successfully")
    return _model

def build_document_text(record):
    make = record.get("data.make") or record.get("make", "")
    model = record.get("data.model") or record.get("model", "")
    component = record.get("data.component") or record.get("component", "")
    summary = record.get("data.summary") or record.get("summary", "")
    parts = [str(p) for p in [make, model, component, summary] if p]
    return " ".join(parts)

def generate_embeddings(texts, normalize=True):
    model = get_model()
    if isinstance(texts, str):
        texts = [texts]
    embeddings = model.encode(texts, normalize_embeddings=normalize)
    logging.info(f"Generated embeddings shape: {embeddings.shape}")
    return embeddings

def cosine_similarity(emb_a, emb_b):
    return util.cos_sim(emb_a, emb_b).item()

def dot_product(emb_a, emb_b):
    return float(np.dot(emb_a, emb_b))

def euclidean_distance(emb_a, emb_b):
    return float(np.linalg.norm(np.array(emb_a) - np.array(emb_b)))