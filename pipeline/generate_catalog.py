#!/usr/bin/env python3
"""Generate a synthetic e-commerce product catalog as JSONL.

Seeded RNG => deterministic output, so the demo is reproducible:

    python pipeline/generate_catalog.py --count 200000 --seed 42 --out data/catalog.jsonl

Each line is one product document matching the schema in schemas.md.
"""
import argparse
import json
import random
from datetime import datetime, timedelta

# (category, subcategory, brands, title templates, price_lo, price_hi)
# {brand} and {model} are substituted per product.
CATALOG = [
    ("Electronics", "Headphones",
     ["Sony", "Bose", "JBL", "Sennheiser", "Audio-Technica"],
     ["{brand} {model} wireless noise cancelling headphones",
      "{brand} {model} bluetooth over-ear headphones with microphone",
      "{brand} {model} true wireless earbuds with charging case",
      "{brand} {model} studio monitor headphones"],
     29.99, 399.99),
    ("Electronics", "TVs",
     ["Samsung", "LG", "Sony", "TCL", "Hisense"],
     ["{brand} {size} inch 4K smart TV with HDR",
      "{brand} {size} inch QLED television with voice remote",
      "{brand} {size} inch OLED smart television"],
     199.99, 2499.99),
    ("Electronics", "Laptops",
     ["Apple", "Dell", "Lenovo", "HP", "Asus"],
     ["{brand} {model} {size} inch laptop with 16GB RAM",
      "{brand} {model} ultrabook {size} inch SSD storage",
      "{brand} {model} gaming laptop RTX graphics {size} inch"],
     499.99, 2999.99),
    ("Electronics", "Smart Watches",
     ["Apple", "Samsung", "Garmin", "Fitbit", "Amazfit"],
     ["{brand} {model} smartwatch with heart rate monitor",
      "{brand} {model} GPS fitness watch waterproof",
      "{brand} {model} smart watch with sleep tracking"],
     49.99, 799.99),
    ("Electronics", "Robot Vacuums",
     ["iRobot", "Roborock", "Eufy", "Shark", "Dyson"],
     ["{brand} {model} robot vacuum with mapping",
      "{brand} {model} self emptying robot vacuum and mop",
      "{brand} {model} lidar navigation robot vacuum"],
     149.99, 1099.99),
    ("Fashion", "Running Shoes",
     ["Nike", "Adidas", "New Balance", "Asics", "Brooks"],
     ["{brand} {model} mens running shoes",
      "{brand} {model} womens trainers with cushioned sole",
      "{brand} {model} lightweight sneakers for marathon"],
     39.99, 249.99),
    ("Fashion", "Backpacks",
     ["Herschel", "JanSport", "Fjallraven", "North Face", "Osprey"],
     ["{brand} {model} laptop backpack water resistant",
      "{brand} {model} hiking backpack {size}L",
      "{brand} {model} canvas daypack with usb port"],
     24.99, 199.99),
    ("Home", "Air Fryers",
     ["Ninja", "Philips", "Cosori", "Instant", "Chefman"],
     ["{brand} {model} {size} quart air fryer with digital display",
      "{brand} {model} dual basket air fryer oven",
      "{brand} {model} compact air fryer for small kitchen"],
     39.99, 299.99),
    ("Home", "Coffee Makers",
     ["Keurig", "Breville", "DeLonghi", "Ninja", "Cuisinart"],
     ["{brand} {model} drip coffee maker with thermal carafe",
      "{brand} {model} espresso machine with milk frother",
      "{brand} {model} single serve coffee maker"],
     29.99, 899.99),
    ("Sports", "Yoga Mats",
     ["Manduka", "Lululemon", "Gaiam", "Jade", "BalanceFrom"],
     ["{brand} {model} extra thick yoga mat non slip",
      "{brand} {model} eco friendly exercise mat with strap",
      "{brand} {model} pro yoga mat {size}mm"],
     14.99, 129.99),
    ("Sports", "Dumbbells",
     ["Bowflex", "PowerBlock", "CAP", "Yes4All", "REP"],
     ["{brand} {model} adjustable dumbbell set",
      "{brand} {model} hex dumbbell pair rubber coated",
      "{brand} {model} kettlebell cast iron"],
     19.99, 549.99),
    ("Toys", "Building Sets",
     ["LEGO", "Mega Construx", "Knex", "Magna-Tiles", "Melissa & Doug"],
     ["{brand} {model} building block set {size} pieces",
      "{brand} {model} creative construction toy for kids",
      "{brand} {model} stem building set ages 6+"],
     9.99, 349.99),
]

DESCRIPTIONS = [
    "Great value for the price. {title} delivers reliable performance for everyday use.",
    "Top rated {title}. Free shipping and easy returns included with every order.",
    "New model {title} with improved design and longer battery life. Customer favorite.",
    "{title} — built to last with premium materials and a 2 year warranty.",
    "Bestseller: {title}. Thousands of five star reviews from verified buyers.",
]

MODEL_PREFIX = ["X", "Pro", "Air", "Max", "Ultra", "Lite", "Plus", "Prime"]


def make_model(rng):
    return f"{rng.choice(MODEL_PREFIX)}-{rng.randint(100, 999)}{rng.choice('ABCD')}"


def generate(count, seed):
    rng = random.Random(seed)
    base_date = datetime(2022, 1, 1)
    for i in range(count):
        cat, sub, brands, templates, lo, hi = rng.choice(CATALOG)
        brand = rng.choice(brands)
        model = make_model(rng)
        size = rng.choice([32, 40, 43, 50, 55, 65, 75]) if "inch" in templates[0] or "{size}" in " ".join(templates) else None
        title = rng.choice(templates).format(brand=brand, model=model, size=size or rng.randint(3, 8))
        # clean up leftover placeholder when template had no {size}
        title = title.replace("  ", " ").strip()
        price = round(rng.uniform(lo, hi), 2)
        rating = round(min(5.0, max(1.0, rng.gauss(4.2, 0.7))), 1)
        review_count = int(rng.lognormvariate(4.5, 1.5))
        yield {
            "id": f"p{i+1:07d}",
            "title": title,
            "description": rng.choice(DESCRIPTIONS).format(title=title),
            "brand": brand,
            "category": cat,
            "subcategory": sub,
            "price": price,
            "rating": rating,
            "review_count": review_count,
            "in_stock": rng.random() < 0.92,
            "created_at": (base_date + timedelta(days=rng.randint(0, 1400))).strftime("%Y-%m-%d"),
        }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=200000)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    n = 0
    with open(args.out, "w") as f:
        for doc in generate(args.count, args.seed):
            f.write(json.dumps(doc) + "\n")
            n += 1
            if n % 50000 == 0:
                print(f"  wrote {n} ...")
    print(f"done: {n} products -> {args.out}")


if __name__ == "__main__":
    main()
