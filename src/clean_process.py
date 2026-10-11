"""Clean, process and feature-engineer the sales dataset using Pandas/NumPy."""
import pandas as pd
import numpy as np
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
RAW = BASE / "data" / "sales_customer_data.csv"
CLEAN = BASE / "data" / "sales_cleaned.csv"

def load() -> pd.DataFrame:
    df = pd.read_csv(RAW, parse_dates=["order_date"])
    print(f"Raw: {df.shape} | missing:\n{df.isna().sum()[df.isna().sum()>0]}")
    return df

def clean(df: pd.DataFrame) -> pd.DataFrame:
    # 1. Deduplicate
    before = len(df)
    df = df.drop_duplicates(subset=["order_id"], keep="first").copy()
    print(f"Removed {before-len(df):,} duplicate orders")

    # 2. Types + missing values
    df["payment_method"] = df["payment_method"].fillna(df["payment_method"].mode()[0])
    df["gender"] = df["gender"].fillna(df["gender"].mode()[0])
    df["discount_pct"] = df["discount_pct"].fillna(0)
    df["age"] = df["age"].fillna(df["age"].median()).astype(int)

    # 3. Sanity filters (outliers / invalid)
    df = df[(df["quantity"] > 0) & (df["unit_price"] > 0) & (df["total_amount"] > 0)]
    df = df[(df["age"] >= 13) & (df["age"] <= 90)]
    # Cap extreme totals at 99.5th pct as outlier flag (keep row, flag it)
    cap = df["total_amount"].quantile(0.995)
    df["is_outlier"] = (df["total_amount"] > cap).astype(int)

    # 4. Recompute total to guarantee consistency (NumPy vectorised)
    df["total_amount"] = np.round(
        df["unit_price"].to_numpy() * df["quantity"].to_numpy()
        * (1 - df["discount_pct"].to_numpy() / 100), 2,
    )

    # 5. Feature engineering
    df["order_month"] = df["order_date"].dt.to_period("M").astype(str)
    df["order_year"] = df["order_date"].dt.year
    df["day_of_week"] = df["order_date"].dt.day_name()
    df["is_weekend"] = df["order_date"].dt.weekday.isin([5, 6]).astype(int)
    df["revenue_bucket"] = pd.cut(
        df["total_amount"], bins=[0, 500, 2000, 10000, float("inf")],
        labels=["Low", "Medium", "High", "Premium"],
    )
    df["age_group"] = pd.cut(
        df["age"], bins=[0, 25, 35, 50, 100],
        labels=["18-25", "26-35", "36-50", "50+"],
    )
    # Customer-level: order count per customer -> repeat flag
    counts = df.groupby("customer_id")["order_id"].transform("count")
    df["customer_order_count"] = counts
    df["is_repeat"] = (counts > 1).astype(int)
    df["discounted"] = (df["discount_pct"] > 0).astype(int)

    df = df.sort_values("order_date").reset_index(drop=True)
    return df

def main():
    df = clean(load())
    CLEAN.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(CLEAN, index=False)
    print(f"Cleaned: {df.shape} -> {CLEAN}")
    print(f"Revenue: ₹{df['total_amount'].sum():,.0f} | AOV: ₹{df['total_amount'].mean():,.0f} | Repeat rate: {df['is_repeat'].mean():.1%}")

if __name__ == "__main__":
    main()
