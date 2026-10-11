-- Sales & Customer Behavior: complex SQL queries (Postgres / SQLite compatible)
-- Table: sales(order_id, order_date, customer_id, age, gender, region,
--   product_category, product_name, quantity, unit_price, discount_pct,
--   total_amount, payment_method, sales_channel, customer_segment)

-- 0. Schema (run once)
CREATE TABLE IF NOT EXISTS sales (
  order_id TEXT PRIMARY KEY,
  order_date DATE NOT NULL,
  customer_id INTEGER NOT NULL,
  age INTEGER,
  gender TEXT,
  region TEXT,
  product_category TEXT,
  product_name TEXT,
  quantity INTEGER,
  unit_price NUMERIC,
  discount_pct NUMERIC DEFAULT 0,
  total_amount NUMERIC,
  payment_method TEXT,
  sales_channel TEXT,
  customer_segment TEXT
);

-- 1. Monthly revenue, orders, AOV + MoM growth (window function)
WITH monthly AS (
  SELECT strftime('%Y-%m', order_date) AS ym,
         SUM(total_amount) AS revenue,
         COUNT(*) AS orders
  FROM sales GROUP BY 1
)
SELECT ym, revenue, orders, ROUND(revenue/orders, 2) AS aov,
       ROUND(100.0*(revenue - LAG(revenue) OVER (ORDER BY ym))/LAG(revenue) OVER (ORDER BY ym), 2) AS mom_growth_pct
FROM monthly ORDER BY ym;

-- 2. Top 5 products per category by revenue (RANK window)
WITH ranked AS (
  SELECT product_category, product_name,
         SUM(total_amount) AS revenue,
         RANK() OVER (PARTITION BY product_category ORDER BY SUM(total_amount) DESC) AS rnk
  FROM sales GROUP BY 1, 2
)
SELECT * FROM ranked WHERE rnk <= 5 ORDER BY product_category, rnk;

-- 3. Customer RFM-lite + repeat segmentation
WITH cust AS (
  SELECT customer_id,
         MAX(order_date) AS last_order,
         COUNT(*) AS frequency,
         SUM(total_amount) AS monetary,
         AVG(total_amount) AS avg_order
  FROM sales GROUP BY 1
)
SELECT customer_id, frequency, monetary, ROUND(avg_order,2) AS aov,
       CASE WHEN frequency >= 5 THEN 'Champion'
            WHEN frequency >= 3 THEN 'Loyal'
            WHEN frequency = 2 THEN 'Repeat'
            ELSE 'One-time' END AS behavior_segment
FROM cust ORDER BY monetary DESC LIMIT 20;

-- 4. Region x Channel matrix with share of total (CTE + window)
WITH m AS (
  SELECT region, sales_channel, SUM(total_amount) AS revenue, COUNT(*) AS orders
  FROM sales GROUP BY 1, 2
)
SELECT region, sales_channel, revenue, orders,
       ROUND(100.0*revenue/SUM(revenue) OVER (), 2) AS pct_of_total
FROM m ORDER BY revenue DESC;

-- 5. Discount effectiveness: does discount lift quantity/AOV?
SELECT
  CASE WHEN discount_pct > 0 THEN 'Discounted' ELSE 'Full price' END AS price_type,
  COUNT(*) AS orders, ROUND(AVG(quantity),2) AS avg_qty,
  ROUND(AVG(total_amount),2) AS aov, ROUND(SUM(total_amount),2) AS revenue
FROM sales GROUP BY 1;

-- 6. Cohort retention: first-purchase month vs repeat rate
WITH firsts AS (
  SELECT customer_id, MIN(strftime('%Y-%m', order_date)) AS cohort FROM sales GROUP BY 1
)
SELECT f.cohort,
       COUNT(DISTINCT f.customer_id) AS customers,
       ROUND(AVG(CASE WHEN s.cnt > 1 THEN 1.0 ELSE 0 END), 3) AS repeat_rate
FROM firsts f JOIN (SELECT customer_id, COUNT(*) AS cnt FROM sales GROUP BY 1) s
  ON s.customer_id = f.customer_id
GROUP BY 1 ORDER BY 1;

-- 7. Premium vs Regular segment comparison with age bands
SELECT customer_segment,
       CASE WHEN age < 26 THEN '18-25' WHEN age < 36 THEN '26-35'
            WHEN age < 51 THEN '36-50' ELSE '50+' END AS age_group,
       COUNT(*) AS orders, ROUND(SUM(total_amount),2) AS revenue,
       ROUND(AVG(total_amount),2) AS aov
FROM sales GROUP BY 1, 2 ORDER BY 1, revenue DESC;

-- 8. Weekend vs weekday + payment-method performance
SELECT period, payment_method, COUNT(*) AS orders, SUM(total_amount) AS revenue
FROM (SELECT *, CASE WHEN strftime('%w', order_date) IN ('0','6') THEN 'Weekend' ELSE 'Weekday' END AS period FROM sales)
GROUP BY 1, 2 ORDER BY revenue DESC;
