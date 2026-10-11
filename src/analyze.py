"""Analyze cleaned data: KPIs, trends, RFM-lite, and charts for Tableau cross-check."""
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
CLEAN = BASE / "data" / "sales_cleaned.csv"
OUT = BASE / "outputs"
OUT.mkdir(parents=True, exist_ok=True)

def main():
    df = pd.read_csv(CLEAN, parse_dates=["order_date"])
    lines = []

    # ---- KPIs ----
    kpis = {
        "total_orders": len(df),
        "total_revenue": df["total_amount"].sum(),
        "aov": df["total_amount"].mean(),
        "unique_customers": df["customer_id"].nunique(),
        "repeat_rate": df["is_repeat"].mean(),
        "avg_discount": df["discount_pct"].mean(),
    }
    lines.append("=== KPIs ===")
    for k, v in kpis.items():
        lines.append(f"{k}: {v:,.2f}")

    # ---- Aggregations ----
    monthly = df.groupby("order_month")["total_amount"].agg(["sum", "count"]).tail(12)
    by_cat = df.groupby("product_category")["total_amount"].agg(["sum", "count", "mean"]).sort_values("sum", ascending=False)
    by_region = df.groupby("region")["total_amount"].agg(["sum", "count", "mean"]).sort_values("sum", ascending=False)
    by_channel = df.groupby("sales_channel")["total_amount"].sum().sort_values(ascending=False)
    by_segment = df.groupby("customer_segment").agg(revenue=("total_amount", "sum"), orders=("order_id", "count"),
                                                     repeat_rate=("is_repeat", "mean"))
    # Discount effectiveness: discounted vs full-price AOV + volume
    disc = df.groupby("discounted")["total_amount"].agg(["mean", "count", "sum"])

    lines += ["\n=== Revenue by Category ===\n" + by_cat.to_string(),
              "\n=== Revenue by Region ===\n" + by_region.to_string(),
              "\n=== Revenue by Channel ===\n" + by_channel.to_string(),
              "\n=== Segment behavior ===\n" + by_segment.to_string(),
              "\n=== Discount effectiveness (0=full price,1=discounted) ===\n" + disc.to_string(),
              "\n=== Last 12 months ===\n" + monthly.to_string()]

    # Top-10 products
    top = df.groupby(["product_category", "product_name"])["total_amount"].sum().sort_values(ascending=False).head(10)
    lines.append("\n=== Top 10 products by revenue ===\n" + top.to_string())

    # Correlation insight
    corr = df[["quantity", "unit_price", "discount_pct", "total_amount", "age"]].corr(numeric_only=True)
    lines.append("\n=== Correlation ===\n" + corr.round(2).to_string())

    (OUT / "insights.txt").write_text("\n".join(lines))
    print("\n".join(lines[:20]))

    # ---- Charts ----
    sns.set_theme(style="whitegrid")
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    df.groupby("order_month")["total_amount"].sum().plot(ax=axes[0, 0], title="Monthly Revenue Trend")
    axes[0, 0].tick_params(axis="x", rotation=45)
    by_cat["sum"].plot.bar(ax=axes[0, 1], title="Revenue by Category")
    by_region["sum"].plot.bar(ax=axes[1, 0], title="Revenue by Region", color="teal")
    df["sales_channel"].value_counts().plot.pie(ax=axes[1, 1], autopct="%1.0f%%", title="Orders by Channel")
    plt.tight_layout()
    plt.savefig(OUT / "dashboard_preview.png", dpi=120)
    print(f"\nSaved outputs/insights.txt + outputs/dashboard_preview.png")

if __name__ == "__main__":
    main()
