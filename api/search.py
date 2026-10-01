"""Core search endpoint: full-text + filters + facets + sorting."""
from fastapi import APIRouter

from api import config
from api.client import get_client
from api.models import FacetBucket, Facets, SearchHit, SearchRequest, SearchResponse

router = APIRouter()

SORTS = {
    "price_asc": [{"price": "asc"}],
    "price_desc": [{"price": "desc"}],
    "rating": [{"rating": "desc"}, {"review_count": "desc"}],
    "newest": [{"created_at": "desc"}],
}


def build_body(req: SearchRequest) -> dict:
    must = []
    if req.query.strip():
        must.append({
            "multi_match": {
                "query": req.query,
                "fields": ["title^3", "description", "brand.text^2"],
                "type": "best_fields",
            }
        })
    else:
        must.append({"match_all": {}})

    filters = []
    if req.category:
        filters.append({"terms": {"category": req.category}})
    if req.subcategory:
        filters.append({"terms": {"subcategory": req.subcategory}})
    if req.brand:
        filters.append({"terms": {"brand": req.brand}})
    price_range = {}
    if req.price_min is not None:
        price_range["gte"] = req.price_min
    if req.price_max is not None:
        price_range["lte"] = req.price_max
    if price_range:
        filters.append({"range": {"price": price_range}})
    if req.min_rating is not None:
        filters.append({"range": {"rating": {"gte": req.min_rating}}})
    if req.in_stock_only:
        filters.append({"term": {"in_stock": True}})

    body = {
        "query": {"bool": {"must": must, "filter": filters}},
        "aggs": {
            "categories": {"terms": {"field": "category", "size": 20}},
            "brands": {"terms": {"field": "brand", "size": 20}},
            "price_ranges": {
                "range": {
                    "field": "price",
                    "ranges": [
                        {"key": "under-25", "to": 25},
                        {"key": "25-to-100", "from": 25, "to": 100},
                        {"key": "100-to-500", "from": 100, "to": 500},
                        {"key": "over-500", "from": 500},
                    ],
                }
            },
        },
        "from": (req.page - 1) * req.page_size,
        "size": req.page_size,
        "track_total_hits": True,
    }
    if req.sort in SORTS:
        body["sort"] = SORTS[req.sort]
    return body


@router.post("/search", response_model=SearchResponse)
def search(req: SearchRequest):
    client = get_client()
    body = build_body(req)
    res = client.search(index=config.INDEX, body=body)

    hits = [
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
    aggs = res.get("aggregations", {})
    facets = Facets(
        categories=[FacetBucket(key=b["key"], count=b["doc_count"]) for b in aggs.get("categories", {}).get("buckets", [])],
        brands=[FacetBucket(key=b["key"], count=b["doc_count"]) for b in aggs.get("brands", {}).get("buckets", [])],
        price_ranges=[FacetBucket(key=b["key"], count=b["doc_count"]) for b in aggs.get("price_ranges", {}).get("buckets", [])],
    )
    return SearchResponse(
        total=res["hits"]["total"]["value"],
        page=req.page,
        page_size=req.page_size,
        took_ms=res.get("took", 0),
        hits=hits,
        facets=facets,
    )
