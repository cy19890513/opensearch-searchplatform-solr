# Search API

```bash
pip install -r api/requirements.txt
cd api && uvicorn main:app --reload   # http://localhost:8000
```

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | cluster info |
| `POST` | `/search` | full-text + filters + facets + sort + pagination |
| `GET` | `/suggest?q=` | autocomplete (PR #5) |
| `GET` | `/similar/{id}` | more-like-this (PR #5) |
| `POST` | `/hybrid-search` | BM25 + vector hybrid (PR #8) |

## Example

```bash
curl -s localhost:8000/search -H 'Content-Type: application/json' -d '{
  "query": "wireless headphones",
  "brand": ["Sony", "Bose"],
  "price_max": 300,
  "min_rating": 4.0,
  "in_stock_only": true,
  "sort": "rating",
  "page": 1,
  "page_size": 10
}' | python3 -m json.tool
```

Interactive docs: http://localhost:8000/docs
