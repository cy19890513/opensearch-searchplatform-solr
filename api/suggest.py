"""Autocomplete endpoint backed by the edge-ngram sub-field."""
from typing import List

from fastapi import APIRouter, Query
from pydantic import BaseModel

from api import config
from api.client import get_client

router = APIRouter()


class Suggestion(BaseModel):
    id: str
    title: str
    brand: str
    price: float


@router.get("/suggest", response_model=List[Suggestion])
def suggest(q: str = Query(..., min_length=2, max_length=100)):
    client = get_client()
    res = client.search(
        index=config.INDEX,
        body={
            "query": {"match": {"title.autocomplete": q}},
            "size": 8,
            "_source": ["title", "brand", "price"],
        },
    )
    return [
        Suggestion(
            id=h["_id"],
            title=h["_source"]["title"],
            brand=h["_source"]["brand"],
            price=h["_source"]["price"],
        )
        for h in res["hits"]["hits"]
    ]
