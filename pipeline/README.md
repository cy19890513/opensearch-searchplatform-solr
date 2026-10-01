# Pipeline

## Generate a synthetic catalog

```bash
python pipeline/generate_catalog.py --count 200000 --seed 42 --out data/catalog.jsonl
```

Seeded RNG: same seed => same catalog. 12 subcategories across
Electronics / Fashion / Home / Sports / Toys, realistic brands, prices,
ratings and stock flags.

## Ingest a real catalog

See `schemas.md`, then:

```bash
python pipeline/load_csv.py --in products.csv --out data/catalog.jsonl
```

## Index into OpenSearch

```bash
bash scripts/create-index.sh        # create the products index (PR #3)
python pipeline/bulk_index.py --file data/catalog.jsonl
```
