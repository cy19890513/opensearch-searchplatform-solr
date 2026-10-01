#!/usr/bin/env python3
"""Latency benchmark: run queries.txt against the search API, report p50/p99.

    python eval/benchmark.py [--base http://localhost:8000] [--out eval/results.md]
"""
import argparse
import statistics
import time
import urllib.request
import json


def post_search(base, query):
    req = urllib.request.Request(
        f"{base}/search",
        data=json.dumps({"query": query, "page_size": 20}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    t0 = time.perf_counter()
    with urllib.request.urlopen(req, timeout=30) as r:
        d = json.load(r)
    dt = (time.perf_counter() - t0) * 1000
    return dt, d["total"], d["took_ms"]


def pct(data, p):
    s = sorted(data)
    k = (len(s) - 1) * p / 100
    f, c = int(k), int(k) + 1
    return s[f] if f == c else s[f] + (s[c] - s[f]) * (k - f)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://localhost:8000")
    ap.add_argument("--queries", default="eval/queries.txt")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    queries = [l.strip() for l in open(args.queries) if l.strip()]
    lat, os_took = [], []
    print(f"running {len(queries)} queries ...")
    for qtext in queries:
        dt, total, took = post_search(args.base, qtext)
        lat.append(dt)
        os_took.append(took)
        print(f"  {dt:7.1f} ms  hits={total:<7} {qtext}")

    lines = [
        "# Benchmark results",
        "",
        f"Queries: {len(queries)} | endpoint: POST /search (page_size=20)",
        "",
        "| metric | end-to-end (ms) | opensearch took (ms) |",
        "|--------|-----------------|-----------------------|",
        f"| p50    | {pct(lat, 50):.1f} | {pct(os_took, 50):.1f} |",
        f"| p99    | {pct(lat, 99):.1f} | {pct(os_took, 99):.1f} |",
        f"| mean   | {statistics.mean(lat):.1f} | {statistics.mean(os_took):.1f} |",
        f"| max    | {max(lat):.1f} | {max(os_took):.1f} |",
    ]
    report = "\n".join(lines)
    print("\n" + report)
    if args.out:
        open(args.out, "w").write(report + "\n")
        print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
