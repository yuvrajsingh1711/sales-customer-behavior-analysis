# Tableau Dashboard — poori guide (Hinglish)

Tumhara data ready hai: `data/sales_cleaned.csv` (55,000 rows).
Reference images isi folder me hain:
- `D1_Executive_Overview.png` — jaisa Dashboard 1 dikhna chahiye
- `D2_Customer_Behavior.png` — jaisa Dashboard 2 dikhna chahiye
- `D3_Discount_Efficiency.png` — jaisa Dashboard 3 dikhna chahiye

## Step 0 — Tableau Public install (free)
1. tableau.com/products/public se Tableau Public download karo
2. Open karo → **Text File** → `data/sales_cleaned.csv` select karo
3. Check karo 55,000 rows aayi. `order_date` = Date, `order_month` = String dikhega

## Step 1 — Calculated Fields (3 fields banao)
Sheet → right-click Data pane → **Create Calculated Field**:

```
// 1. AOV
SUM([total_amount]) / COUNT([order_id])

// 2. Repeat Rate
AVG([is_repeat])

// 3. MoM Growth %
(ZN(SUM([total_amount])) - LOOKUP(ZN(SUM([total_amount])), -1))
/ ABS(LOOKUP(ZN(SUM([total_amount])), -1))
```
Format: AOV = Currency (Rs), Repeat Rate aur MoM = Percentage, 1 decimal.

## Step 2 — Dashboard 1: Executive Overview (photo: D1)
Sheets banao:
1. **KPI cards**: alag-alag sheet me `SUM(total_amount)`, `COUNT(order_id)`, AOV, `COUNTD(customer_id)`, Repeat Rate ko Text me daalo
2. **Monthly Trend**: Columns = `order_month` (right-click → Exact Date continuous nahi, Month Year value), Rows = `SUM(total_amount)`, mark = Line + circles
3. **Category Bar**: Rows = `product_category`, Columns = `SUM(total_amount)`, sort descending
4. **Region Bar**: same, `region` se
5. Dashboard → New → size 1366x768 → sab sheets drag karo + Filter add karo: `order_year`, `region`, `product_category`, `sales_channel` (Apply to all)

## Step 3 — Dashboard 2: Customer Behavior (photo: D2)
1. **Segment Donut**: `customer_segment` → Color + Angle(`COUNT(order_id)`), Pie mark
2. **Repeat by Age**: Columns = `age_group`, Rows = Repeat Rate field, Bar
3. **Top Products**: Rows = `product_name`, Columns = `SUM(total_amount)`, filter Top 8 by revenue
4. **Scatter**: Columns = `customer_order_count`, Rows = `total_amount`, Color = `region`, sample 3000 points (Data → filter ya extract me limit)

## Step 4 — Dashboard 3: Discount & Efficiency (photo: D3)
1. **AOV bar**: `discounted` (0/1 ko alias do: Full price / Discounted) vs AOV
2. **Heatmap**: Rows = `region`, Columns = `sales_channel`, Color+Label = `SUM(total_amount)`
3. **Weekday vs Weekend**: `is_weekend` (0/1 → Weekday/Weekend) vs revenue, Bar
4. **Payment bar**: `payment_method` vs revenue, sort ascending
- Insight text box add karo: "Full-price AOV Rs.20,688 vs Discounted Rs.17,956 — discount se volume badhta hai, margin nahi. Marketplace+South sabse weak hai."

## Step 5 — Publish (resume/GitHub ke liye)
1. File → **Save to Tableau Public** → account banao/login
2. Jo public link mile, use `README.md` aur resume me daalo
3. Dashboard ke screenshots (ya isi folder ki D1/D2/D3 PNGs) GitHub repo me upload karo

## Data types check (galti ho to)
- `order_date` → Date, `total_amount/unit_price` → Number decimal
- `is_repeat/is_weekend/discounted/is_outlier` → Number (0/1), alias laga lo
- `order_month` → agar sort gadbad ho to `order_date` se Month-Year bana lo: `DATETRUNC('month',[order_date])`

## Interview me bolne wali line
"Electronics 68% revenue deta hai, Online sabse bada channel hai, discount wala AOV full-price se ~13% kam hai — isliye weak channel/region se spend hatakar focus segment me lagane se ~15% efficiency ka scope nikla."
