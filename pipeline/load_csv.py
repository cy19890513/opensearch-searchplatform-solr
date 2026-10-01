#!/usr/bin/env python3
"""Convert a real product catalog CSV into the JSONL schema used by this project.

Expected CSV columns (see schemas.md):

    id,title,description,brand,category,subcategory,price,rating,review_count,in_stock,created_at

Usage:
    python pipeline/load_csv.py --in products.csv --out data/catalog.jsonl
"""
import argparse
import csv
import json


def to_bool(v):
    return str(v).strip().lower() in ("1", "true", "yes", "y", "in_stock")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    n = 0
    with open(args.inp, newline="", encoding="utf-8") as fin, open(args.out, "w", encoding="utf-8") as fout:
        for row in csv.DictReader(fin):
            doc = {
                "id": row["id"].strip(),
                "title": row["title"].strip(),
                "description": (row.get("description") or "").strip(),
                "brand": row["brand"].strip(),
                "category": row["category"].strip(),
                "subcategory": (row.get("subcategory") or "").strip(),
                "price": float(row["price"]),
                "rating": float(row.get("rating") or 0),
                "review_count": int(float(row.get("review_count") or 0)),
                "in_stock": to_bool(row.get("in_stock", "true")),
                "created_at": (row.get("created_at") or "2024-01-01").strip(),
            }
            fout.write(json.dumps(doc, ensure_ascii=False) + "\n")
            n += 1
    print(f"done: {n} products -> {args.out}")


if __name__ == "__main__":
    main()
