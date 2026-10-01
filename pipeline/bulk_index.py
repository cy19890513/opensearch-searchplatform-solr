#!/usr/bin/env python3
"""Bulk-index a catalog JSONL file into OpenSearch.

    python pipeline/bulk_index.py --file data/catalog.jsonl [--index products]
"""
import argparse
import json

from opensearchpy import OpenSearch
from opensearchpy.helpers import bulk


def get_client(host):
    return OpenSearch(
        hosts=[{"host": host, "port": 9200, "scheme": "https"}],
        http_auth=("admin", "SearchDemo123!"),
        verify_certs=False,
        ssl_show_warn=False,
    )


def docs(path, index):
    with open(path, encoding="utf-8") as f:
        for line in f:
            d = json.loads(line)
            yield {"_index": index, "_id": d["id"], "_source": d}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--file", required=True)
    ap.add_argument("--index", default="products")
    ap.add_argument("--host", default="localhost")
    ap.add_argument("--chunk", type=int, default=2000)
    args = ap.parse_args()

    client = get_client(args.host)
    ok, failed = bulk(
        client, docs(args.file, args.index),
        chunk_size=args.chunk, request_timeout=120,
    )
    print(f"indexed ok={ok} failed={len(failed)}")
    for err in failed[:5]:
        print("FAILED:", err)


if __name__ == "__main__":
    main()
