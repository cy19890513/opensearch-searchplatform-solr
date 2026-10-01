#!/usr/bin/env python3
"""Generate vector embeddings for the catalog (offline step for hybrid search).

Uses sentence-transformers/all-MiniLM-L6-v2 (384 dims, ~90MB download on
first run). Output JSONL has one extra field, `embedding`, per product:

    python pipeline/embed.py --in data/catalog.jsonl --out data/catalog-emb.jsonl

Then create the v2 index and bulk-index the enriched file:

    INDEX=products-v2 bash scripts/create-index.sh   # needs products-index-v2.json
    python pipeline/bulk_index.py --file data/catalog-emb.jsonl --index products-v2
"""
import argparse
import json

BATCH = 256


def main():
    from sentence_transformers import SentenceTransformer

    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="inp", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--model", default="all-MiniLM-L6-v2")
    args = ap.parse_args()

    model = SentenceTransformer(args.model)
    docs = [json.loads(l) for l in open(args.inp, encoding="utf-8")]
    texts = [f"{d['title']}. {d['description']}" for d in docs]

    n = 0
    with open(args.out, "w", encoding="utf-8") as fout:
        for i in range(0, len(texts), BATCH):
            vecs = model.encode(texts[i:i + BATCH], show_progress_bar=False)
            for d, v in zip(docs[i:i + BATCH], vecs):
                d["embedding"] = [float(x) for x in v]
                fout.write(json.dumps(d) + "\n")
                n += 1
            print(f"  embedded {n}/{len(docs)} ...")
    print(f"done: {n} docs -> {args.out}")


if __name__ == "__main__":
    main()
