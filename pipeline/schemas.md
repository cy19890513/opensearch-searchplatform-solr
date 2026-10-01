# Product document schema

Every product — synthetic or real — is one JSON object per line (JSONL)
with these fields:

| Field | Type | Example | Notes |
|-------|------|---------|-------|
| `id` | string (keyword) | `p0000042` | unique |
| `title` | string (text) | `Sony X-200B wireless noise cancelling headphones` | primary search field |
| `description` | string (text) | `Top rated ...` | secondary search field |
| `brand` | string (keyword) | `Sony` | facet + filter |
| `category` | string (keyword) | `Electronics` | facet + filter |
| `subcategory` | string (keyword) | `Headphones` | facet + filter |
| `price` | float | `249.99` | range filter, sort, range facet |
| `rating` | float 0–5 | `4.5` | filter, sort |
| `review_count` | integer | `1234` | popularity signal |
| `in_stock` | boolean | `true` | filter |
| `created_at` | date `YYYY-MM-DD` | `2024-03-11` | recency |

## Ingesting a real catalog

Export your catalog as CSV with the column names above, then:

```bash
python pipeline/load_csv.py --in products.csv --out data/catalog.jsonl
python pipeline/bulk_index.py --file data/catalog.jsonl
```

`load_csv.py` is strict about `id`, `title`, `brand`, `category`, `price`
and lenient about the rest (sane defaults are applied).
