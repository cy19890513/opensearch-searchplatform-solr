#!/bin/bash
# Smoke-test the search API. Requires: containers up, index built, API running.
set -euo pipefail
BASE="${BASE:-http://localhost:8000}"

echo "== /health =="
curl -sf "$BASE/health" | python3 -m json.tool | head -8

echo "== /search =="
curl -sf "$BASE/search" -H 'Content-Type: application/json' -d '{
  "query": "wireless headphones", "page_size": 3
}' | python3 -c "import json,sys; d=json.load(sys.stdin); print('total:', d['total'], '| top hit:', d['hits'][0]['title'])"

echo "== /suggest =="
curl -sf "$BASE/suggest?q=sony%20wh" | python3 -c "
import json,sys
for s in json.load(sys.stdin): print('-', s['title'])"

echo "== /similar =="
ID=$(curl -sf "$BASE/search" -H 'Content-Type: application/json' -d '{"query":"yoga mat","page_size":1}' | python3 -c "import json,sys; print(json.load(sys.stdin)['hits'][0]['id'])")
curl -sf "$BASE/similar/$ID?size=3" | python3 -c "
import json,sys
for s in json.load(sys.stdin): print('-', s['title'])"

echo SMOKE_OK
