# OpenSearch index

## Analyzers

- `product_analyzer` (used for `title`, `description`):
  `standard` tokenizer -> `lowercase` -> `asciifolding` -> `synonym_graph`
  (`opensearch/synonyms.txt`, mounted read-only into the container).
- `autocomplete_analyzer` (used for `title.autocomplete`):
  `standard` tokenizer -> `lowercase` -> `asciifolding` -> `edge_ngram(2,20)`.
  Queries against this field use the plain `standard` analyzer so a
  3-character prefix matches the indexed n-grams.

Synonyms are baked in at index time: after editing `synonyms.txt`,
recreate the index and reindex.

## Create the index

```bash
# after pulling this PR, recreate containers so the synonyms mount applies:
make down && make up
bash scripts/create-index.sh
python pipeline/bulk_index.py --file data/catalog.jsonl
```

## Inspect the analyzer

```bash
curl -sku admin:SearchDemo123! -X POST https://localhost:9200/products/_analyze \
  -H 'Content-Type: application/json' \
  -d '{"analyzer": "product_analyzer", "text": "sneakers for runners"}'
# "trainers", "running shoes" appear as synonym tokens
```
