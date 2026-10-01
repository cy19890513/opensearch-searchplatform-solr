#!/bin/bash
# CI sanity checks: byte-compile all Python, validate all JSON configs.
set -euo pipefail

echo "== python compile =="
if compgen -G "pipeline/*.py" > /dev/null || compgen -G "api/*.py" > /dev/null || compgen -G "eval/*.py" > /dev/null; then
  python3 -m compileall -q pipeline api eval
  echo "compile OK"
else
  echo "no python sources yet, skipping"
fi

echo "== json validation =="
found=0
while IFS= read -r -d '' f; do
  found=1
  python3 -c "import json; json.load(open('$f'))" && echo "OK $f"
done < <(find opensearch solr -name '*.json' -print0 2>/dev/null || true)
[ "$found" -eq 0 ] && echo "no json configs yet, skipping"

echo ALL_CHECKS_PASSED
