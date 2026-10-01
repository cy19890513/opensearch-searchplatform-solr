# OpenSearch vs Solr comparison

Same dataset (`data/catalog.jsonl`), same host, same query set
(`eval/queries.txt`). This is an apples-to-apples operational comparison,
not a scientific benchmark.

## Index into both

```bash
# OpenSearch
bash scripts/create-index.sh
python pipeline/bulk_index.py --file data/catalog.jsonl

# Solr (schemaless _default configset, precreated 'products' core)
python scripts/index-solr.py --file data/catalog.jsonl
```

## Query both

OpenSearch (via the API):

```bash
python eval/benchmark.py --out eval/results.md
```

Solr (equivalent: edismax across title/description/brand, 20 rows):

```bash
for q in "wireless headphones" "4k tv 55 inch" "yoga mat non slip"; do
  curl -s "http://localhost:8983/solr/products/select?q=$q&defType=edismax&qf=title%5E3+description+brand%5E2&rows=20&wt=json" \
    | python3 -c "import json,sys; d=json.load(sys.stdin); print(d['response']['numFound'], 'hits')"
done
```

## What to compare

| Dimension | OpenSearch | Solr |
|-----------|-----------|------|
| Indexing throughput (docs/sec) | `bulk_index.py` output | `index-solr.py` output |
| p50/p99 search latency | `eval/results.md` | time the curl loop |
| Config model | JSON index settings + mappings | managed-schema / configsets |
| Analyzer story | `product_analyzer` chain in `products-index.json` | `<analyzer>` chains in schema |
| Synonyms | file mounted into container | `synonyms.txt` in core conf |
| Ops | Docker Compose, security on by default | `solr-precreate`, no auth by default |

## Honest notes

- The Solr side uses the schemaless default configset on purpose: it shows
  how far zero-config gets you, and where you start needing a real schema
  (edge n-grams for autocomplete, synonym filters) — which is exactly what
  PR #3 hand-builds on the OpenSearch side.
- Single-node numbers on a laptop say nothing about distributed behavior.
  The interesting comparison is developer experience, not a 5% latency delta.
