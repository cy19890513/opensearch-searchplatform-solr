# OpenSearch Search Platform (with Solr comparison)

A portfolio-grade e-commerce product search platform demonstrating hands-on
search-engineering skills: OpenSearch indexing, custom analyzers, Query DSL,
faceted search, autocomplete, and hybrid (BM25 + vector) retrieval — with a
head-to-head comparison against Apache Solr on the same dataset.

```
                        ┌─────────────────────┐
                        │     OpenSearch      │
┌──────────────┐ bulk   │  products index     │
│ Data Pipeline│───────▶│  - custom analyzers │
│ (generate /   │        │  - synonyms, edge   │
│  ingest)     │        │    n-grams, k-NN    │
└──────────────┘        └────────┬────────────┘
                                 │
┌──────────────┐ same dataset    │  ┌──────────────┐
│ Solr         │◀── for ──────────┘  │  Search API  │
│ (comparison) │   benchmarking      │  FastAPI     │
└──────────────┘                     └──────┬───────┘
                                           │
                                    ┌──────▼───────┐
                                    │   Web UI     │
                                    │  demo search │
                                    └──────────────┘
```

## Quickstart

```bash
make up                                  # start OpenSearch, Dashboards, Solr
python pipeline/generate_catalog.py --count 200000 --out data/catalog.jsonl
bash scripts/create-index.sh             # create the products index
python pipeline/bulk_index.py --file data/catalog.jsonl
cd api && uvicorn main:app --reload       # search API on :8000
open http://localhost:8000/ui            # demo UI
```

## PR roadmap

| PR | Content |
|----|---------|
| #1 | Project scaffolding: Docker Compose, CI, docs |
| #2 | Data pipeline: synthetic catalog generator + CSV ingest |
| #3 | OpenSearch index: mappings, custom analyzers, bulk indexing |
| #4 | Search API core: `POST /search` with filters, facets, sorting |
| #5 | `GET /suggest` autocomplete + `GET /similar/{id}` |
| #6 | Demo web UI |
| #7 | Benchmarks (p50/p99) + OpenSearch vs Solr comparison |
| #8 | Hybrid search: BM25 + k-NN vector retrieval |

## API overview

| Endpoint | Description |
|----------|-------------|
| `POST /search` | Full-text search with filters, facets, sorting, pagination |
| `GET /suggest?q=` | Autocomplete suggestions |
| `GET /similar/{id}` | More-like-this recommendations |
| `POST /hybrid-search` | BM25 + vector hybrid retrieval (PR #8) |
| `GET /health` | Health check |

## Layout

- `pipeline/` — catalog generator, CSV ingest, bulk indexer, embeddings
- `opensearch/` — index settings/mappings, synonyms
- `api/` — FastAPI search service
- `ui/` — demo web frontend
- `eval/` — benchmark queries, latency harness, relevance notes
- `scripts/` — operational helpers
