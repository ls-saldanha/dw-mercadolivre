"""
app.py — Streamlit dashboard for dw-mercadolivre.

Reads from gold.mart_sales and renders three charts:
1. Daily revenue (BRL and USD) — dual-axis line chart
2. Revenue by category — grouped bar chart
3. 7-day rolling revenue by category — line chart
"""

import os

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from urllib.parse import urlparse

load_dotenv()

st.set_page_config(page_title="dw-mercadolivre", layout="wide")
st.title("dw-mercadolivre — Sales Dashboard")


@st.cache_data(ttl=300)
def load_data() -> pd.DataFrame:
    """Load mart_sales from Postgres. Cached for 5 minutes."""
    supabase_url = os.environ["SUPABASE_URL"]
    password = os.environ["SUPABASE_DB_PASSWORD"]
    host = urlparse(supabase_url).hostname
    project_ref = host.split(".")[0]
    db_url = f"postgresql+psycopg2://postgres:{password}@db.{project_ref}.supabase.co:5432/postgres"

    engine = create_engine(db_url)
    with engine.connect() as conn:
        df = pd.read_sql(text("SELECT * FROM gold.mart_sales ORDER BY sale_date, product_category"), conn)
    return df


df = load_data()

if df.empty:
    st.warning("No data in gold.mart_sales. Run the pipeline first.")
    st.stop()

st.caption(f"Data from {df['sale_date'].min()} to {df['sale_date'].max()} · {len(df)} rows")

# ── Chart 1: Daily revenue BRL and USD (dual-axis line) ──────────────────────
st.subheader("Daily Revenue — BRL vs USD")

daily = df.groupby("sale_date")[["revenue_brl", "revenue_usd"]].sum().reset_index()

fig1 = go.Figure()
fig1.add_trace(go.Scatter(
    x=daily["sale_date"], y=daily["revenue_brl"],
    name="Revenue (BRL)", line=dict(color="#00B4D8"), yaxis="y1"
))
fig1.add_trace(go.Scatter(
    x=daily["sale_date"], y=daily["revenue_usd"],
    name="Revenue (USD)", line=dict(color="#F4A261", dash="dash"), yaxis="y2"
))
fig1.update_layout(
    yaxis=dict(title="BRL", tickprefix="R$ "),
    yaxis2=dict(title="USD", overlaying="y", side="right", tickprefix="$ "),
    legend=dict(orientation="h", y=1.1),
    margin=dict(l=0, r=0, t=30, b=0),
    height=350,
)
st.plotly_chart(fig1, width='stretch')

# ── Chart 2: Revenue by category (grouped bar) ───────────────────────────────
st.subheader("Revenue by Category")

cat = df.groupby("product_category")["revenue_brl"].sum().sort_values(ascending=False).reset_index()

fig2 = go.Figure(go.Bar(
    x=cat["product_category"],
    y=cat["revenue_brl"],
    marker_color=["#00B4D8", "#F4A261", "#90E0EF", "#E9C46A", "#2A9D8F"],
    text=cat["revenue_brl"].apply(lambda v: f"R$ {v:,.0f}"),
    textposition="outside",
))
fig2.update_layout(
    yaxis=dict(title="Revenue (BRL)", tickprefix="R$ "),
    margin=dict(l=0, r=0, t=10, b=0),
    height=350,
)
st.plotly_chart(fig2, width='stretch')

# ── Chart 3: 7-day rolling revenue by category ───────────────────────────────
st.subheader("7-Day Rolling Revenue by Category")

COLORS = ["#00B4D8", "#F4A261", "#90E0EF", "#E9C46A", "#2A9D8F"]
fig3 = go.Figure()
for i, cat_name in enumerate(df["product_category"].unique()):
    cat_df = df[df["product_category"] == cat_name].sort_values("sale_date")
    fig3.add_trace(go.Scatter(
        x=cat_df["sale_date"],
        y=cat_df["revenue_7d_rolling_brl"],
        name=cat_name,
        line=dict(color=COLORS[i % len(COLORS)]),
    ))
fig3.update_layout(
    yaxis=dict(title="7-Day Rolling Revenue (BRL)", tickprefix="R$ "),
    legend=dict(orientation="h", y=1.1),
    margin=dict(l=0, r=0, t=30, b=0),
    height=350,
)
st.plotly_chart(fig3, width='stretch')

# ── Summary metrics ──────────────────────────────────────────────────────────
st.divider()
col1, col2, col3, col4 = st.columns(4)
col1.metric("Total Revenue (BRL)", f"R$ {df['revenue_brl'].sum():,.0f}")
col2.metric("Total Revenue (USD)", f"$ {df['revenue_usd'].sum():,.0f}")
col3.metric("Total Orders", f"{df['order_count'].sum():,}")
col4.metric("Units Sold", f"{df['units_sold'].sum():,}")
