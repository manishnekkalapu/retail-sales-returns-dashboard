# dashboards/streamlit_app.py
"""
Simple Streamlit dashboard for Retail Sales & Returns Dashboard starter project.

Reads: data/sample_sales.csv
Shows: KPIs (GMV, AOV, Returns Rate), timeseries, top products by revenue and returns.
"""

import streamlit as st
import pandas as pd
import sqlite3
import os
from datetime import datetime

st.set_page_config(page_title="Retail Sales & Returns Dashboard", layout="wide")

ROOT = os.path.join(os.path.dirname(__file__), "..")  # repo root
DATA_CSV = os.path.join(ROOT, "data", "sample_sales.csv")
DB_PATH = os.path.join(ROOT, "data", "retail.db")

st.title("Retail Sales & Returns Dashboard — Starter")

# Load data helper: prefer SQLite if exists (from etl), otherwise CSV
@st.cache_data
def load_data():
    if os.path.exists(DB_PATH):
        try:
            conn = sqlite3.connect(DB_PATH)
            df = pd.read_sql("SELECT * FROM sales", conn)
            conn.close()
            return df
        except Exception:
            pass
    if os.path.exists(DATA_CSV):
        df = pd.read_csv(DATA_CSV)
        # normalize column names if necessary
        df.columns = [c.strip() for c in df.columns]
        # ensure date column exists
        if "date" not in df.columns and "OrderID" in df.columns:
            # no date in sample CSV — create a synthetic date index for demo
            rng = pd.date_range(end=pd.Timestamp.today(), periods=len(df))
            df["date"] = rng.strftime("%Y-%m-%d")
        # ensure numeric columns
        if "Total" not in df.columns and {"Quantity", "UnitPrice"}.issubset(df.columns):
            df["Total"] = df["Quantity"].astype(float) * df["UnitPrice"].astype(float)
        return df
    st.error("No data found. Upload data/sample_sales.csv or run src/etl.py to create data/retail.db.")
    return pd.DataFrame()

df = load_data()
if df.empty:
    st.stop()

# Basic preprocessing
df["date"] = pd.to_datetime(df["date"])
if "returned" not in df.columns:
    df["returned"] = 0
df["returned"] = df["returned"].astype(int)

# Sidebar filters
st.sidebar.header("Filters")
min_date = df["date"].min()
max_date = df["date"].max()
date_range = st.sidebar.date_input("Date range", [min_date.date(), max_date.date()])
product_filter = st.sidebar.multiselect("Products / SKUs", options=sorted(df["product"].unique()), default=None)
category_filter = st.sidebar.multiselect("Category", options=sorted(df["Category"].unique()) if "Category" in df.columns else [], default=None)

# Apply filters
start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
mask = (df["date"] >= start) & (df["date"] <= end)
if product_filter:
    mask &= df["product"].isin(product_filter)
if category_filter:
    mask &= df["Category"].isin(category_filter)
df_f = df.loc[mask].copy()

# KPIs
total_revenue = df_f["Total"].sum()
total_orders = df_f.shape[0]
aov = total_revenue / total_orders if total_orders else 0
returns = df_f["returned"].sum()
returns_rate = (returns / total_orders) if total_orders else 0

col1, col2, col3, col4 = st.columns(4)
col1.metric("GMV (Total Revenue)", f"£{total_revenue:,.2f}")
col2.metric("Orders", f"{int(total_orders):,}")
col3.metric("AOV", f"£{aov:,.2f}")
col4.metric("Returns Rate", f"{returns_rate:.2%}")

st.markdown("---")

# Time series
st.subheader("Revenue & Orders Over Time")
ts = df_f.groupby(df_f["date"].dt.to_period("D")).agg(revenue=("Total", "sum"), orders=("OrderID", "count")).reset_index()
ts["date"] = ts["date"].dt.to_timestamp()
if ts.empty:
    st.info("No timeseries data for selected filters.")
else:
    st.line_chart(ts.set_index("date")[["revenue", "orders"]])

st.markdown("---")

# Top products tables
st.subheader("Top Products by Revenue")
top_rev = df_f.groupby("product").agg(revenue=("Total", "sum"), units_sold=("Quantity", "sum"), returns=("returned", "sum")).reset_index()
top_rev = top_rev.sort_values("revenue", ascending=False).head(10)
st.table(top_rev)

st.subheader("Top Products by Returns")
top_returns = df_f.groupby("product").agg(returns=("returned", "sum"), orders=("OrderID", "count")).reset_index()
top_returns["return_rate"] = (top_returns["returns"] / top_returns["orders"]).fillna(0)
top_returns = top_returns.sort_values("returns", ascending=False).head(10)
st.table(top_returns)

st.markdown("---")
st.write("Repository: `retail-sales-returns-dashboard` — run `python src/etl.py` to build `data/retail.db` or upload `data/sample_sales.csv`.")
