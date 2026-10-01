#!/bin/bash
# (Re)create the products index in OpenSearch.
set -euo pipefail
OS_URL="${OS_URL:-https://localhost:9200}"
AUTH="admin:SearchDemo123!"
INDEX="${INDEX:-products}"

curl -sku "$AUTH" -X DELETE "$OS_URL/$INDEX" > /dev/null 2>&1 || true
curl -sku "$AUTH" -X PUT "$OS_URL/$INDEX" \
  -H 'Content-Type: application/json' \
  --data-binary @opensearch/products-index.json | python3 -m json.tool
