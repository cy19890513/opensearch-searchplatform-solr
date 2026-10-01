"""More-like-this recommendations for a given product id."""
from typing import List

from fastapi import APIRouter, HTTPException

from api import config
from api.client import get_client
from api.models import SearchHit

router = APIRouter()


@router.get("/similar/{doc_id}", response_model=List[SearchHit])
def similar(doc_id: str, size: int = 10):
    client = get_client()
    try:
        doc = client.get(index=config.INDEX, id=doc_id)["_source"]
    except Exception:
        raise HTTPException(status_code=404, detail=f"product {doc_id} not found")

    res = client.search(
        index=config.INDEX,
        body={
            "query": {
                "bool": {
                    "must": [
                        {
                            "more_like_this": {
                                "fields": ["title", "description"],
                                "like": [{"_id": doc_id}],
                                "min_term_freq": 1,
                                "min_doc_freq": 2,
                            }
                        }
                    ],
                    "must_not": [{"term": {"_id": doc_id}}],
                    "filter": [
                        {"term": {"category": doc["category"]}},
                        {"term": {"in_stock": True}},
                    ],
                }
            },
            "size": size,
        },
    )
    return [
        SearchHit(
            id=h["_id"],
            title=h["_source"]["title"],
            brand=h["_source"]["brand"],
            category=h["_source"]["category"],
            subcategory=h["_source"].get("subcategory", ""),
            price=h["_source"]["price"],
            rating=h["_source"]["rating"],
            review_count=h["_source"].get("review_count", 0),
            in_stock=h["_source"].get("in_stock", True),
            score=h["_score"] or 0.0,
        )
        for h in res["hits"]["hits"]
    ]
