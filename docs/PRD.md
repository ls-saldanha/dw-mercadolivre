# dw-mercadolivre — Project Specification v1.1

**Version:** 1.1 · May 2026

> A daily-refreshing Data Warehouse using the Medallion architecture — Bronze, Silver, Gold — with real FX data, dbt transforms, and a live dashboard.

---

## 1. What We're Building

This project is a portfolio-grade Data Warehouse. It ingests data from two sources every day, cleans and transforms that data through three distinct layers, and surfaces the results in an interactive dashboard.

**The two data sources:**

- **Synthetic sales generator** — a Python script that produces realistic fake orders, customers, and products. It runs daily and appends new records, simulating how a real e-commerce backend would feed data into a warehouse.
- **Bacen PTAX API** — the Brazilian Central Bank publishes daily USD/BRL exchange rates through a public, open endpoint. One HTTP request, one row, no authentication required.

**The three transformation layers** follow the Medallion architecture, an industry-standard pattern for organising data in a warehouse:

| Layer | What it contains | Postgres schema |
|---|---|---|
| Bronze | Raw data exactly as it arrived. Nothing changed, nothing removed. | `bronze` |
| Silver | Cleaned and typed. Duplicates removed, columns standardised, a price-tier classification added. | `silver` |
| Gold | Business-ready aggregates. One sales mart with daily revenue in both BRL and USD, order counts, and 7-day rolling averages. | `gold` |

The Streamlit dashboard reads from the Gold layer and shows three charts: a daily revenue line (BRL and USD on dual axes), a category breakdown, and a 7-day rolling average.

> **Goal:** run `python run_pipeline.py` and have fresh data in the dashboard within minutes. No manual steps, no partial runs.

---

## 2. Technology Stack

| Component | Tool | Why this choice |
|---|---|---|
| Database | Supabase (PostgreSQL) | Managed Postgres with a generous free tier. No infrastructure to maintain. |
| Object storage | AWS S3 | Raw Parquet files land here before loading into Postgres. Industry-standard for data lake storage. |
| Ingestion | Python 3.13 | `httpx` for HTTP, `pandas` for data manipulation, `pydantic` for API response validation, `boto3` for S3. |
| Transformation | dbt-core + dbt-postgres | SQL-based transformations with built-in testing, documentation, and lineage tracking. |
| Orchestration | Manual script (v1.1) | `run_pipeline.py` orchestrates all steps. Prefect replaces this in v2 once the pipeline is proven. |
| Dashboard | Streamlit | Python-native, no new language to learn, deploys free on Streamlit Cloud. Metabase replaces it in v2. |
| Secrets | `.env` locally | Never committed. Prefect blocks manage secrets in v2. |

---

## 3. Data Flow

Every pipeline run follows this sequence, in order:

1. **Synthetic generator** writes today's sales, customers, and products as Parquet files to S3 under `bronze/internal_*/ingestion_date=YYYY-MM-DD/`
2. **Bacen fetcher** calls the PTAX endpoint and writes today's FX rate to S3 under `bronze/bacen_ptax/ingestion_date=YYYY-MM-DD/`
3. **Bronze loader** reads all of today's Parquet files from S3 and inserts them into the `bronze` schema. Each load is idempotent — running it twice on the same day overwrites, never duplicates.
4. **`dbt build`** runs `dbt run` and `dbt test` in a single command. If any test fails, the run stops. Gold tables are never updated with bad data.
5. **Dashboard** reads from `gold.mart_sales` and renders the charts.

> **Key design decision:** the pipeline is intentionally sequential with no parallelism in v1.1. Each step depends on the previous one succeeding. This makes debugging straightforward and failures obvious.

---

## 4. Data Model

### 4.1 Bronze — raw landing

Bronze tables mirror the source data exactly, with one addition: an `_ingested_at TIMESTAMPTZ` column added on load. S3 files are partitioned by source and date.

| Table | Source | Key columns |
|---|---|---|
| `bronze.internal_sales` | Synthetic generator | `order_id`, `customer_id`, `product_sku`, `quantity`, `unit_price`, `order_date` |
| `bronze.internal_customers` | Synthetic generator | `customer_id`, `name`, `city`, `state`, `signup_date` |
| `bronze.internal_products` | Synthetic generator | `product_sku`, `name`, `category`, `unit_price` |
| `bronze.bacen_ptax` | Bacen API | `cotacao_date`, `bid_rate`, `ask_rate` |

### 4.2 Silver — conformed and typed

| Model | Key transformations |
|---|---|
| `stg_sales` | Typed columns, deduplicated on `order_id`, `total_amount` computed (`quantity × unit_price`) |
| `stg_customers` | Typed columns, snake_case normalisation |
| `stg_products` | Typed columns, `price_tier` label added (cheap / mid / premium by price quantile) |
| `stg_bacen_ptax` | Typed, forward-filled for weekends and holidays using the most recent business day rate |

### 4.3 Gold — `mart_sales`

One row per `(date, product_category)`. This is what the dashboard reads.

| Column | Description |
|---|---|
| `sale_date` | Date of the orders |
| `product_category` | Category from the product dimension |
| `revenue_brl` | Sum of `total_amount` in BRL |
| `revenue_usd` | `revenue_brl` divided by the day's PTAX bid rate |
| `order_count` | Count of distinct orders |
| `units_sold` | Sum of quantities |
| `avg_order_value_brl` | `revenue_brl / order_count` |
| `revenue_7d_rolling_brl` | 7-day rolling sum using a window function |

---

## 5. Data Quality

dbt tests run on every pipeline execution as part of `dbt build`. A test failure halts the run — Gold is never updated with bad data.

**Silver tests (every model):**
- `not_null` on the primary key column
- `unique` on the primary key column
- `relationships` test where foreign key references exist
- `accepted_values` on categorical columns (`price_tier`, currency codes)

**Gold tests (`mart_sales`):**
- `not_null` on `revenue_brl` and `order_count`
- Singular test: `revenue_brl >= 0` on every row — negative revenue indicates a join or calculation error

> **Why tests matter:** the pipeline runs daily without anyone watching it. Tests catch schema drift, API changes, or calculation bugs before they silently corrupt the dashboard.

---

## 6. Repository Structure

```
dw-mercadolivre/
├── run_pipeline.py              # Single entrypoint. Runs all five steps.
├── CLAUDE.md                    # Working agreement with Claude Code
├── pyproject.toml               # Python dependencies (uv)
├── .env.example                 # Template env vars, no real values
├── .pre-commit-config.yaml      # gitleaks + hygiene hooks
├── ingestion/
│   ├── bacen/                   # PTAX fetcher
│   ├── synthetic/               # Fake data generator
│   └── common/                  # s3.py, loader.py
├── dbt/
│   ├── models/staging/          # Four Silver models
│   └── models/marts/            # mart_sales
├── dashboard/
│   └── app.py                   # Streamlit dashboard
├── security/
│   ├── README.md                # IAM + gitleaks setup
│   └── iam-policy-s3.json
└── docs/
    ├── PRD.md
    ├── ARCHITECTURE.md
    ├── ROADMAP.md
    ├── time-estimate.md
    └── decisions/               # 11 Architecture Decision Records
```

---

## 7. Milestones

Each milestone has a specific acceptance criterion. The next one doesn't start until the current one is verified.

| # | Milestone | Done when |
|---|---|---|
| M1 | Foundation — Supabase, S3, credentials, pre-commit | Smoke test runs green end-to-end on a clean checkout |
| M2 | Synthetic generator | Three Parquet files in S3. Re-running the same day overwrites idempotently. |
| M3 | Bacen fetcher | Today's FX rate in S3. Weekend/holiday handled gracefully. |
| M4 | Bronze loader | All Bronze tables populated. Re-running doesn't duplicate rows. |
| M5 | dbt Silver | Four staging models in `silver` schema. All tests pass. |
| M6 | dbt Gold | `mart_sales` in `gold` schema. Tests pass. Numbers look sensible. |
| M7 | Dashboard | `streamlit run dashboard/app.py` opens with current data. |
| M8 | Wiring and docs | A stranger could clone the repo and run it within 30 minutes. |

---

## 8. Security Baseline

This is a public repository. Three concrete practices prevent the predictable mistakes.

1. **Pre-commit secret scanning with gitleaks.** Every commit is scanned before it reaches GitHub. Bypassing requires an explicit override, which creates an audit trail.
2. **Explicit naming of high-privilege keys.** The Supabase master credential is `SUPABASE_SERVICE_ROLE_KEY`, not `SUPABASE_KEY`. The name signals what's at stake every time it appears.
3. **Least-privilege IAM policy.** The AWS user has exactly three permissions: `ListBucket`, `GetObject`, and `PutObject` on the project bucket only.

> **If a secret leaks:** rotate the credential immediately at the source. History scrubbing is cosmetic — rotation is the real fix.

---

## 9. Deliberately Out of Scope

| Feature | Why deferred | When |
|---|---|---|
| Mercado Livre API | OAuth + rate-limit handling + schema validation is three new tools at once. Easier after the stack is familiar. | v2, phase A |
| Prefect orchestration | Adds a separate mental model on top of an unfamiliar language. v1.1 uses a plain Python script. | v2, phase B |
| Metabase BI layer | Requires Docker and BI tool setup. Streamlit covers the need in v1.1. | v2, phase C |
| dbt CI on pull requests | One hour of setup, high-credibility signal. Deferred to keep v1.1 focused. | Any time after M8 |
| Incremental dbt models | Full rebuilds are fine at this data volume. | v2 |
| `mart_pricing`, `mart_customers` | Need Mercado Livre (pricing) and more SQL comfort (RFM). | v2, phase A |

---

## 10. Roadmap to v2

Three independent phases. Each is separately scoped and shippable.

### Phase A — Mercado Livre integration (15–25 hours)

Adds the live competitor pricing story. Registers a Mercado Livre developer app, implements OAuth, fetches product listings for 2–3 categories daily, and models the data into two new Gold marts: `mart_pricing` (competitive index per SKU per day, in BRL and USD) and `mart_customers` (RFM segmentation and churn indicators).

### Phase B — Prefect orchestration (8–15 hours)

Replaces `run_pipeline.py` with five Prefect flows on a daily schedule. Adds retries, failure alerts, and an observability UI. Most valuable after Phase A — three sources on different cadences is the reason to have a proper scheduler.

### Phase C — Metabase BI layer (5–10 hours)

Replaces Streamlit with Metabase OSS in Docker, connected to the Gold schema through a read-only Postgres role. Three dashboards, one per Gold mart. The self-service BI story lives here.

---

## 11. Definition of Done

v1.1 is complete when **all** of these are true:

- [ ] `python run_pipeline.py` runs end-to-end without errors
- [ ] All dbt tests pass on the most recent run
- [ ] The Streamlit dashboard shows current data and loads in under 5 seconds
- [ ] dbt docs are published to GitHub Pages with a connected lineage graph
- [ ] The README has a pitch, architecture diagram, setup instructions, and screenshots
- [ ] The repository is public on GitHub
- [ ] A blog post is published covering the project, the decisions, and what comes next
- [ ] You can explain any function or model in an interview — notes are fine, reading off the screen is not

The last item is the one most people skip when AI writes the code. Don't.

---

*dw-mercadolivre v1.1 · May 2026*
