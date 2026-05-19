# Milestones 6 & 7 — dbt Gold + Streamlit Dashboard

## 2026-05-19 Checkpoint: mart_sales built, dashboard running

**What we built:**
- `mart_sales` Gold table: one row per (sale_date, product_category), with revenue in BRL and USD, order counts, and a 7-day rolling revenue window.
- Streamlit dashboard reading from Gold: three charts + four summary metrics.

**Files touched:**
- `dbt/models/marts/mart_sales.sql` — Gold model
- `dbt/models/marts/schema.yml` — not_null tests
- `dbt/tests/assert_positive_revenue.sql` — singular test
- `dashboard/app.py` — Streamlit app
- `pyproject.toml` / `uv.lock` — streamlit, plotly added

**New concepts introduced:**

- **`ref()` in Gold** — `{{ ref('stg_internal_sales') }}` links mart_sales to its Silver dependencies. dbt's DAG guarantees Silver always runs before Gold.
- **Correlated subquery for FX lookup** — for each aggregated row, a subquery finds the most recent PTAX rate on or before the sale date. Handles weekends without a date spine: `where cotacao_date <= sale_date order by cotacao_date desc limit 1`.
- **`rows between 6 preceding and current row`** — window frame that accumulates the current row plus the 6 rows before it, partitioned by category and ordered by date. This is the 7-day rolling sum.
- **`NULLIF` for safe division** — `revenue_brl / nullif(bid_rate, 0)` avoids a division-by-zero error if the FX rate is ever missing. Returns NULL instead of crashing.
- **Gold materialised as `table`** — staging models are views (computed on demand). The mart is a physical table because the dashboard queries it on every load; we don't want to re-run all the joins each time.
- **`@st.cache_data(ttl=300)`** — Streamlit decorator that caches the `load_data()` result for 5 minutes. Without it, every user interaction would re-query Postgres.
- **Plotly dual-axis line chart** — `yaxis2=dict(overlaying="y", side="right")` overlays a second Y axis on the same plot. BRL on the left, USD dashed on the right.
- **Singular dbt test** — `assert_positive_revenue.sql` returns rows where `revenue_brl < 0`. dbt passes the test only when the query returns zero rows. This is the pattern for business-rule assertions that don't fit into generic test types.

**Patterns reused:**
- Same `_build_db_url()` logic as `loader.py` to derive the Supabase connection string.
- Same `source → typed → deduplicated → aggregated → final` CTE layering pattern, applied to Gold.

**Numbers verified:** 5 rows (5 categories × 1 day). Electronics R$93k, apparel R$59k, home R$39k, health R$9.7k, books R$7.4k. `revenue_usd` = `revenue_brl / 5.0087` ✓. Rolling 7d = day total (only 1 day of data) ✓.

**Next step:** M8 — wire up `run_pipeline.py` end-to-end, write README, publish.
