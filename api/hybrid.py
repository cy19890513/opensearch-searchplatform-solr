"""Hybrid search: BM25 keyword retrieval fused with k-NN vector retrieval.

Score fusion: min-max normalize each list to [0,1], then
    final = alpha * knn_score + (1 - alpha) * bm25_score
"""
from typing import List

from fastapi import APIRouter
from sentence_transformers import SentenceTransformer

from api import config
from api.client import get_client
from api.models import HybridRequest, HybridResponse, SearchHit

router = APIRouter()

_model = None


def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def normalize(scores: dict) -> dict:
    if not scores:
        return {}
    lo, hi = min(scores.values()), max(scores.values())
    if hi == lo:
        return {k: 1.0 for k in scores}
    return {k: (v - lo) / (hi - lo) for k, v in scores.items()}


def to_hit(h, score) -> SearchHit:
    s = h["_source"]
    return SearchHit(
        id=h["_id"], title=s["title"], brand=s["brand"],
        category=s["category"], subcategory=s.get("subcategory", ""),
        price=s["price"], rating=s["rating"],
        review_count=s.get("review_count", 0),
        in_stock=s.get("in_stock", True), score=round(score, 4),
    )


@router.post("/hybrid-search", response_model=HybridResponse)
def hybrid_search(req: HybridRequest):
    client = get_client()
    vec = get_model().encode(req.query).tolist()

    knn_res = client.search(index=config.INDEX, body={
        "query": {"knn": {"embedding": {"vector": vec, "k": req.page_size * 5}}},
        "size": req.page_size * 5,
    })
    bm25_res = client.search(index=config.INDEX, body={
        "query": {"multi_match": {
            "query": req.query,
            "fields": ["title^3", "description", "brand.text^2"],
            "type": "best_fields",
        }},
        "size": req.page_size * 5,
    })

    knn_scores = normalize({h["_id"]: h["_score"] for h in knn_res["hits"]["hits"]})
    bm25_scores = normalize({h["_id"]: h["_score"] for h in bm25_res["hits"]["hits"]})
    docs = {h["_id"]: h for h in knn_res["hits"]["hits"] + bm25_res["hits"]["hits"]}

    fused = {
        did: req.alpha * knn_scores.get(did, 0.0) + (1 - req.alpha) * bm25_scores.get(did, 0.0)
        for did in docs
    }
    ranked = sorted(fused.items(), key=lambda kv: kv[1], reverse=True)[:req.page_size]
    hits: List[SearchHit] = [to_hit(docs[did], score) for did, score in ranked]
    return HybridResponse(
        total=len(fused), took_ms=knn_res.get("took", 0) + bm25_res.get("took", 0),
        hits=hits, alpha=req.alpha,
    )
