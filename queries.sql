-- queries.sql
-- Core KPI queries for Retail Sales & Returns Dashboard
-- Run these against the SQLite table named `sales` created by etl.py

-- 1) Gross Merchandise Value (GMV) by day
SELECT
  date AS day,
  SUM(Total) AS gmv,
  COUNT(*) AS orders,
  SUM(quantity) AS units_sold
FROM sales
GROUP BY date
ORDER BY date;

-- 2) Average Order Value (AOV) for last 30 days
SELECT
  ROUND(SUM(Total) * 1.0 / NULLIF(COUNT(*),0), 2) AS aov,
  SUM(Total) AS total_revenue,
  COUNT(*) AS total_orders
FROM sales
WHERE date >= date('now','-30 days');

-- 3) Overall returns rate
SELECT
  SUM(CASE WHEN returned = 1 THEN 1 ELSE 0 END) * 1.0 / NULLIF(COUNT(*),0) AS returns_rate,
  SUM(CASE WHEN returned = 1 THEN 1 ELSE 0 END) AS total_returns,
  COUNT(*) AS total_orders
FROM sales;

-- 4) Top 10 SKUs / Products by revenue
SELECT product AS sku, SUM(Total) AS revenue, SUM(quantity) AS units_sold,
       SUM(CASE WHEN returned = 1 THEN 1 ELSE 0 END) AS returns,
       ROUND(SUM(CASE WHEN returned = 1 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*),1),2) AS return_rate
FROM sales
GROUP BY product
ORDER BY revenue DESC
LIMIT 10;

-- 5) Top 10 SKUs by returns count
SELECT product AS sku, SUM(CASE WHEN returned = 1 THEN 1 ELSE 0 END) AS returns,
       COUNT(*) AS orders,
       ROUND(SUM(CASE WHEN returned = 1 THEN 1 ELSE 0 END) * 100.0 / NULLIF(COUNT(*),1),2) AS return_rate
FROM sales
GROUP BY product
ORDER BY returns DESC
LIMIT 10;
