"""Pydantic request/response models for the search API."""
from typing import List, Optional

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = ""
    category: List[str] = Field(default_factory=list)
    subcategory: List[str] = Field(default_factory=list)
    brand: List[str] = Field(default_factory=list)
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    min_rating: Optional[float] = None
    in_stock_only: bool = False
    sort: str = "relevance"  # relevance | price_asc | price_desc | rating | newest
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


class SearchHit(BaseModel):
    id: str
    title: str
    brand: str
    category: str
    subcategory: str
    price: float
    rating: float
    review_count: int
    in_stock: bool
    score: float


class FacetBucket(BaseModel):
    key: str
    count: int


class Facets(BaseModel):
    categories: List[FacetBucket] = Field(default_factory=list)
    brands: List[FacetBucket] = Field(default_factory=list)
    price_ranges: List[FacetBucket] = Field(default_factory=list)


class SearchResponse(BaseModel):
    total: int
    page: int
    page_size: int
    took_ms: int
    hits: List[SearchHit]
    facets: Facets


class HybridRequest(BaseModel):
    query: str
    page_size: int = Field(default=20, ge=1, le=100)
    alpha: float = Field(default=0.5, ge=0.0, le=1.0)  # weight of vector score


class HybridResponse(BaseModel):
    total: int
    took_ms: int
    alpha: float
    hits: List[SearchHit]
