# Relevance tuning notes

What was tuned, why, and what it changed. No synthetic precision/recall
theater — these are the judgment calls behind `products-index.json` and
`api/search.py`.

## Field boosts

`title^3`, `brand.text^2`, `description` unboosted. Rationale: in product
search the title carries the purchase intent ("sony wireless headphones"),
the description is marketing copy with keyword stuffing, and brand is a
strong intent signal ("nike shoes"). `best_fields` (default) so a match in
the best field dominates rather than summing across fields.

## Synonyms (index-time, `synonym_graph`)

`sneakers ↔ trainers ↔ running shoes`, `tv ↔ television`, etc.
Index-time expansion keeps queries simple and fast; the cost is reindexing
when the list changes (documented in `opensearch/README.md`).
Query-time synonyms would avoid reindexing but complicate scoring.

Observed effect: `trainers` and `running shoes` return the same result set
as `sneakers` — verify with:

```bash
curl -sku admin:SearchDemo123! -X POST https://localhost:9200/products/_analyze \
  -H 'Content-Type: application/json' \
  -d '{"analyzer":"product_analyzer","text":"trainers"}'
```

## Autocomplete

Edge n-grams (2–20) on `title.autocomplete`, queried with the plain
`standard` analyzer. Prefixes of length ≥ 2 match; ranking is still BM25
over the n-gram field, which favors shorter, more popular titles.

## What was deliberately NOT tuned

- BM25 `k1`/`b` left at defaults. Tuning them without labeled judgments is
  numerology; defaults are well-calibrated for short product titles.
- No learning-to-rank / click models — needs real behavioral data, and
  pretending otherwise would be dishonest in a demo.
- `review_count` and `rating` are exposed as sort options and filters, not
  blended into relevance. Blending popularity into the score is a product
  decision, not a relevance default.
