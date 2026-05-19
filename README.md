# dw-mercadolivre

**[dbt docs & lineage graph →](https://ls-saldanha.github.io/dw-mercadolivre/)**

A portfolio-grade Data Warehouse that ingests synthetic e-commerce sales and live USD/BRL exchange rates from Brazil's Central Bank, transforms them through three data layers, and surfaces the results in an interactive dashboard — all triggered by a single command.

```
uv run python run_pipeline.py
```

## What this demonstrates

- **Medallion architecture** (Bronze → Silver → Gold) on PostgreSQL
- **Python ingestion** with Pydantic validation, httpx, and boto3
- **AWS S3** as a raw Parquet data lake, partitioned by date
- **dbt** for SQL transformations, automated testing, and lineage tracking
- **Streamlit** dashboard reading from the Gold layer
- **Security baseline**: pre-commit secret scanning (gitleaks), least-privilege IAM, no secrets in code

## Architecture

```
                   ┌─────────────────────────────────┐
                   │         run_pipeline.py          │
                   └─────────────┬───────────────────┘
                                 │
          ┌──────────────────────┼──────────────────────┐
          ▼                      ▼                      ▼
  synthetic/generator     bacen/fetch.py         (future sources)
  (fake sales, customers,  (PTAX USD/BRL via
   products via Faker)      Bacen OLINDA API)
          │                      │
          └──────────┬───────────┘
                     ▼
              AWS S3 (Parquet)
         bronze/{source}/ingestion_date=YYYY-MM-DD/
                     │
                     ▼
         common/loader.py  ──▶  Postgres: bronze schema
                     │
                     ▼
              dbt build
         ┌───────────────────┐
         │  Silver (views)   │  stg_internal_sales
         │                   │  stg_internal_customers
         │                   │  stg_internal_products
         │                   │  stg_bacen_ptax
         └────────┬──────────┘
                  ▼
         ┌───────────────────┐
         │  Gold (table)     │  mart_sales
         │                   │  (sale_date × category)
         └────────┬──────────┘
                  ▼
         Streamlit dashboard
         (revenue BRL/USD, category breakdown, 7d rolling)
```

## Stack

| Layer | Tool |
|---|---|
| Database | Supabase (PostgreSQL) |
| Object storage | AWS S3 |
| Ingestion | Python 3.13 · httpx · pandas · pydantic · boto3 |
| Transformation | dbt-core · dbt-postgres |
| Dashboard | Streamlit · Plotly |
| Secrets | `.env` (local) · gitleaks pre-commit hook |

## Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) — Python package manager
- A [Supabase](https://supabase.com) project (free tier works)
- An AWS S3 bucket with an IAM user scoped to `ListBucket`, `GetObject`, `PutObject`, `DeleteObject`

## Setup

1. **Clone and install dependencies**

   ```bash
   git clone https://github.com/lucasdev/dw-mercadolivre.git
   cd dw-mercadolivre
   uv sync
   ```

2. **Configure environment variables**

   ```bash
   cp .env.example .env
   # Edit .env with your Supabase and AWS credentials
   ```

   Required variables — see `.env.example` for the full list:
   - `SUPABASE_URL`, `SUPABASE_DB_PASSWORD`, `SUPABASE_SERVICE_ROLE_KEY`
   - `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `AWS_DEFAULT_REGION`, `S3_BUCKET`

3. **Run the pipeline**

   ```bash
   uv run python run_pipeline.py
   ```

   This will:
   - Generate synthetic sales for today → S3
   - Fetch today's USD/BRL rate from Bacen → S3
   - Load all Parquets into Postgres Bronze tables
   - Run dbt build (Silver + Gold transforms + 27 data tests)

4. **Open the dashboard**

   ```bash
   uv run streamlit run dashboard/app.py
   ```

   Open http://localhost:8501

## Running individual steps

```bash
# Ingestion only
uv run python -m ingestion.synthetic.generator
uv run python -m ingestion.bacen.fetch
uv run python -m ingestion.common.loader

# dbt only (from repo root)
uv run dbt build --profiles-dir dbt --project-dir dbt
uv run dbt build --select mart_sales --profiles-dir dbt --project-dir dbt
```

## Project structure

```
ingestion/
  bacen/          PTAX daily FX fetch (Bacen OLINDA API)
  synthetic/      Fake sales / customers / products (Faker)
  common/         s3.py — Parquet helpers; loader.py — S3 → Postgres
dbt/
  models/staging/ Four Silver views (typed, deduplicated)
  models/marts/   mart_sales Gold table
  tests/          Singular SQL tests (business rule assertions)
  macros/         generate_schema_name override
dashboard/
  app.py          Streamlit dashboard
security/
  iam-policy-s3.json  Least-privilege S3 IAM policy
docs/
  PRD.md          Full project specification
  ARCHITECTURE.md Architectural overview
  decisions/      11 Architecture Decision Records
```

## Data model (Gold)

`gold.mart_sales` — one row per `(sale_date, product_category)`:

| Column | Description |
|---|---|
| `sale_date` | Date of the orders |
| `product_category` | electronics / apparel / home / health / books |
| `revenue_brl` | Sum of order totals in BRL |
| `revenue_usd` | `revenue_brl` ÷ PTAX bid rate |
| `order_count` | Distinct order count |
| `units_sold` | Sum of quantities |
| `avg_order_value_brl` | `revenue_brl / order_count` |
| `revenue_7d_rolling_brl` | 7-day rolling sum per category |

## v2 roadmap

Live Mercado Livre API pricing · Prefect orchestration · Metabase BI layer — see [docs/ROADMAP.md](docs/ROADMAP.md).

---

*v1.1 · May 2026*
