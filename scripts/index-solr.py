#!/usr/bin/env python3
"""Index the catalog JSONL into Solr (stdlib only, no extra deps).

Uses the schemaless `_default` configset via the precreated `products` core:

    python scripts/index-solr.py --file data/catalog.jsonl [--solr http://localhost:8983]
"""
import argparse
import json
import urllib.request

BATCH = 1000


def post(solr, docs):
    payload = json.dumps(docs).encode()
    req = urllib.request.Request(
        f"{solr}/solr/products/update/json/docs?commit=true",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        assert r.status == 200, r.read()[:200]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", required=True)
    ap.add_argument("--solr", default="http://localhost:8983")
    args = ap.parse_args()

    batch, n = [], 0
    with open(args.file, encoding="utf-8") as f:
        for line in f:
            batch.append(json.loads(line))
            if len(batch) >= BATCH:
                post(args.solr, batch)
                n += len(batch)
                batch = []
                print(f"  indexed {n} ...")
    if batch:
        post(args.solr, batch)
        n += len(batch)
    print(f"done: {n} docs -> Solr core 'products'")


if __name__ == "__main__":
    main()
