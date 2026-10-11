"""Generate synthetic Sales & Customer Behavior dataset (50,000+ records)."""
import numpy as np
import pandas as pd
from pathlib import Path

N = 55000
SEED = 42
rng = np.random.default_rng(SEED)

OUT = Path(__file__).resolve().parents[1] / "data" / "sales_customer_data.csv"

regions = ["North", "South", "East", "West", "Central"]
categories = {
    "Electronics": ["Headphones", "Smartwatch", "Bluetooth Speaker", "Laptop Stand", "USB-C Hub"],
    "Clothing": ["T-Shirt", "Jeans", "Jacket", "Sneakers", "Hoodie"],
    "Home & Kitchen": ["Air Fryer", "Coffee Maker", "Bedsheet Set", "Cookware Set", "Lamp"],
    "Beauty": ["Moisturizer", "Serum", "Lipstick Set", "Hair Dryer", "Perfume"],
    "Sports": ["Yoga Mat", "Dumbbell Set", "Running Shoes", "Water Bottle", "Gym Bag"],
    "Books": ["Fiction Novel", "Self-Help Book", "Cookbook", "Children Book", "Notebook Set"],
}
channels = ["Online", "Retail Store", "Mobile App", "Marketplace"]
payments = ["Credit Card", "Debit Card", "UPI", "Net Banking", "Wallet", "COD"]
segments = ["New", "Regular", "Premium", "Corporate"]
genders = ["Male", "Female", "Other"]

cat_keys = list(categories.keys())
cat_probs = np.array([0.25, 0.22, 0.18, 0.12, 0.13, 0.10])

order_ids = [f"ORD-{100000+i}" for i in range(N)]
customer_ids = rng.integers(1000, 12000, size=N)  # ~11k unique customers -> repeat behavior
dates = pd.to_datetime(rng.integers(
    pd.Timestamp("2022-01-01").value // 10**9,
    pd.Timestamp("2024-12-31").value // 10**9,
    size=N,
), unit="s")
ages = rng.normal(36, 12, N).round().astype(int).clip(16, 75)
gender = rng.choice(genders, N, p=[0.48, 0.48, 0.04])
region = rng.choice(regions, N, p=[0.25, 0.20, 0.20, 0.20, 0.15])
prod_cat = rng.choice(cat_keys, N, p=cat_probs)
prod_name = [rng.choice(categories[c]) for c in prod_cat]
channel = rng.choice(channels, N, p=[0.40, 0.25, 0.20, 0.15])
payment = rng.choice(payments, N, p=[0.30, 0.20, 0.20, 0.10, 0.10, 0.10])
segment = rng.choice(segments, N, p=[0.35, 0.35, 0.15, 0.15])

base_price = {
    "Electronics": (999, 45000), "Clothing": (299, 4999),
    "Home & Kitchen": (499, 15000), "Beauty": (199, 3500),
    "Sports": (299, 8000), "Books": (99, 1499),
}
unit_price = np.array([rng.uniform(*base_price[c]) for c in prod_cat]).round(2)
quantity = rng.choice([1, 1, 1, 2, 2, 3, 4, 5], size=N)
discount_pct = rng.choice([0, 0, 0, 5, 10, 15, 20, 30], size=N, p=[0.35, 0.15, 0.10, 0.12, 0.10, 0.08, 0.06, 0.04])
total = (unit_price * quantity * (1 - discount_pct / 100)).round(2)

df = pd.DataFrame({
    "order_id": order_ids,
    "order_date": dates.date,
    "customer_id": customer_ids,
    "age": ages,
    "gender": gender,
    "region": region,
    "product_category": prod_cat,
    "product_name": prod_name,
    "quantity": quantity,
    "unit_price": unit_price,
    "discount_pct": discount_pct,
    "total_amount": total,
    "payment_method": payment,
    "sales_channel": channel,
    "customer_segment": segment,
})

# Inject realistic data-quality issues (~5% missing, ~1% dupes)
for col, frac in [("age", 0.02), ("gender", 0.01), ("discount_pct", 0.01), ("payment_method", 0.015)]:
    df.loc[rng.choice(N, int(N*frac), replace=False), col] = np.nan
dupes = df.sample(int(N*0.01), random_state=SEED)
df = pd.concat([df, dupes], ignore_index=True)
df = df.sample(frac=1, random_state=SEED).reset_index(drop=True)  # shuffle

OUT.parent.mkdir(parents=True, exist_ok=True)
df.to_csv(OUT, index=False)
print(f"Saved {len(df):,} rows -> {OUT}")
print(df.head(3).to_string())
