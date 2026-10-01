# Hybrid search (BM25 + k-NN)

Keyword search fails on vocabulary mismatch: `gift for a coffee lover`
matches no product title, but vector search understands the intent.
Hybrid fuses both signals.

## Setup

```bash
pip install -r pipeline/requirements-hybrid.txt   # sentence-transformers (~90MB model on first run)

# 1. embed the catalog (offline, CPU is fine for 200k docs in batches)
python pipeline/embed.py --in data/catalog.jsonl --out data/catalog-emb.jsonl

# 2. create the v2 index (adds the knn_vector field; index.knn=true)
#    create-index.sh reads opensearch/products-index.json by default, so point it at v2:
cp opensearch/products-index-v2.json opensearch/products-index.json
bash scripts/create-index.sh

# 3. index with embeddings, pointed at the v2 index
OS_INDEX=products-v2 python pipeline/bulk_index.py --file data/catalog-emb.jsonl --index products-v2

# 4. run the API against it
OS_INDEX=products-v2 uvicorn main:app --reload --app-dir api
```

## Query

```bash
curl -s localhost:8000/hybrid-search -H 'Content-Type: application/json' -d '{
  "query": "gift for a coffee lover",
  "alpha": 0.7,
  "page_size": 5
}' | python3 -c "
import json,sys
for h in json.load(sys.stdin)['hits']: print(round(h['score'],3), h['title'])"
```

`alpha` blends the signals: `1.0` = pure vector, `0.0` = pure BM25,
`0.5` = even split. Fusion is min-max normalization + weighted sum,
done in Python so the blend is transparent and tunable.

## Try these

| Query | Why hybrid wins |
|-------|-----------------|
| `gift for a coffee lover` | intent, no keyword overlap |
| `quiet headphones for office` | "quiet" ~ noise cancelling (semantic) |
| `cheap 4k television` | price intent + synonym (tv/television) |
| `sneakers` | BM25 already nails this; alpha=0.2 suffices |
