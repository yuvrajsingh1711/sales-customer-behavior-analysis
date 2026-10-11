"""Build 3 Tableau-style dashboards as PNGs (Executive, Customer, Discount)."""
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
DF = pd.read_csv(BASE / "data" / "sales_cleaned.csv", parse_dates=["order_date"])
OUT = BASE / "tableau"
OUT.mkdir(parents=True, exist_ok=True)

sns.set_theme(style="whitegrid")
plt.rcParams.update({"figure.dpi": 130, "font.size": 9})

def fmt_cr(ax):
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x/1e7:.1f} Cr" if x >= 1e7 else f"{x/1e5:.0f}L"))

# ---------- D1: Executive Overview ----------
fig = plt.figure(figsize=(14, 8))
fig.suptitle("Dashboard 1 — Executive Overview | Sales & Customer Behavior", fontsize=14, fontweight="bold", y=0.98)
# KPI strip
rev = DF["total_amount"].sum(); aov = DF["total_amount"].mean()
orders = len(DF); cust = DF["customer_id"].nunique(); rep = DF["is_repeat"].mean()*100
fig.text(0.5, 0.92, f"Revenue Rs. {rev:,.0f}   |   Orders {orders:,}   |   AOV Rs. {aov:,.0f}   |   Customers {cust:,}   |   Repeat {rep:.1f}%",
         ha="center", fontsize=11, bbox=dict(boxstyle="round", fc="#eef4ff"))
gs = fig.add_gridspec(2, 2, hspace=0.4, wspace=0.3, top=0.86, bottom=0.08)
ax1 = fig.add_subplot(gs[0, :])
m = DF.groupby("order_month")["total_amount"].sum()
m.index = pd.to_datetime(m.index)
m = m.sort_index()
ax1.plot(m.index, m.values, marker="o", linewidth=2)
ax1.set_title("Monthly Revenue Trend (2022-2024)"); fmt_cr(ax1); ax1.tick_params(axis="x", rotation=30)
ax2 = fig.add_subplot(gs[1, 0])
DF.groupby("product_category")["total_amount"].sum().sort_values().plot.barh(ax=ax2, color="#2a7de1")
ax2.set_title("Revenue by Category"); ax2.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x/1e7:.0f}Cr"))
ax3 = fig.add_subplot(gs[1, 1])
DF.groupby("region")["total_amount"].sum().sort_values().plot.barh(ax=ax3, color="#0ca678")
ax3.set_title("Revenue by Region"); ax3.xaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{x/1e7:.0f}Cr"))
fig.savefig(OUT / "D1_Executive_Overview.png", bbox_inches="tight")
plt.close(fig)

# ---------- D2: Customer Behavior ----------
fig = plt.figure(figsize=(14, 8))
fig.suptitle("Dashboard 2 — Customer Behavior", fontsize=14, fontweight="bold", y=0.98)
fig.text(0.5, 0.92, "Segment • Age Group Repeat • Top Products • Channel Mix", ha="center", fontsize=10,
         bbox=dict(boxstyle="round", fc="#fff4e6"))
gs = fig.add_gridspec(2, 2, hspace=0.4, wspace=0.3, top=0.86, bottom=0.08)
ax1 = fig.add_subplot(gs[0, 0])
DF["customer_segment"].value_counts().plot.pie(ax=ax1, autopct="%1.0f%%", colors=sns.color_palette("Set2"))
ax1.set_title("Orders by Segment"); ax1.set_ylabel("")
ax2 = fig.add_subplot(gs[0, 1])
rep_age = DF.groupby("age_group", observed=True)["is_repeat"].mean()*100
rep_age.plot.bar(ax=ax2, color="#7048e8")
ax2.set_title("Repeat Rate % by Age Group"); ax2.set_ylim(95, 100)
ax3 = fig.add_subplot(gs[1, 0])
DF.groupby("product_name")["total_amount"].sum().nlargest(8).sort_values().plot.barh(ax=ax3, color="#e67700")
ax3.set_title("Top 8 Products by Revenue")
ax4 = fig.add_subplot(gs[1, 1])
sns.scatterplot(data=DF.sample(3000, random_state=42), x="customer_order_count", y="total_amount",
                hue="region", alpha=0.4, s=10, ax=ax4)
ax4.set_title("Order Frequency vs Spend (3k sample)"); ax4.set_ylim(0, DF["total_amount"].quantile(0.99))
fig.savefig(OUT / "D2_Customer_Behavior.png", bbox_inches="tight")
plt.close(fig)

# ---------- D3: Discount & Efficiency ----------
fig = plt.figure(figsize=(14, 8))
fig.suptitle("Dashboard 3 — Discount & Channel Efficiency (15% insight)", fontsize=14, fontweight="bold", y=0.98)
fig.text(0.5, 0.92, "Full-price AOV Rs. 20,688 vs Discounted Rs. 17,956 → discount drives volume, not margin",
         ha="center", fontsize=10, bbox=dict(boxstyle="round", fc="#e6fcf5"))
gs = fig.add_gridspec(2, 2, hspace=0.4, wspace=0.3, top=0.86, bottom=0.08)
ax1 = fig.add_subplot(gs[0, 0])
DF.groupby("discounted")["total_amount"].mean().rename({0: "Full price", 1: "Discounted"}).plot.bar(ax=ax1, color=["#2a7de1", "#fa5252"])
ax1.set_title("AOV: Full-price vs Discounted"); ax1.tick_params(axis="x", rotation=0)
ax2 = fig.add_subplot(gs[0, 1])
piv = DF.pivot_table(index="region", columns="sales_channel", values="total_amount", aggfunc="sum")
sns.heatmap(piv/1e7, annot=True, fmt=".1f", cmap="YlGnBu", ax=ax2)
ax2.set_title("Revenue (Cr) — Region × Channel")
ax3 = fig.add_subplot(gs[1, 0])
DF.groupby(DF["is_weekend"].map({0: "Weekday", 1: "Weekend"}))["total_amount"].sum().plot.bar(ax=ax3, color="#12b886")
ax3.set_title("Weekday vs Weekend Revenue"); ax3.tick_params(axis="x", rotation=0)
ax4 = fig.add_subplot(gs[1, 1])
DF.groupby("payment_method")["total_amount"].sum().sort_values().plot.barh(ax=ax4, color="#7950f2")
ax4.set_title("Revenue by Payment Method")
fig.savefig(OUT / "D3_Discount_Efficiency.png", bbox_inches="tight")
plt.close(fig)

print("Saved:", sorted(p.name for p in OUT.glob("D*.png")))
