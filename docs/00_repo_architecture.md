# Repository Architecture — `dw-mercadolivre` v1.1

This is the exact folder and file structure you'll create. Each section includes what goes in that file/folder and why.

---

## Root Level

```
dw-mercadolivre/
├── README.md                          # Project overview, setup, screenshots
├── CLAUDE.md                          # Working agreement with Claude Code
├── pyproject.toml                     # Python dependencies (uv)
├── .env.example                       # Template env vars (no real values)
├── .gitignore                         # Excludes .env, __pycache__, .venv, etc.
├── .pre-commit-config.yaml            # gitleaks + hygiene hooks
├── run_pipeline.py                    # Single entrypoint: orchestrates all steps
├── ingestion/                         # Data ingestion layer
├── dbt/                               # Data transformations (Bronze/Silver/Gold)
├── dashboard/                         # Streamlit BI dashboard
├── security/                          # Security setup docs and templates
└── docs/                              # Documentation and decisions
```

---

## `/ingestion` — Data Ingestion

```
ingestion/
├── __init__.py                        # Makes this a Python package
│
├── bacen/
│   └── fetch.py                       # Fetches PTAX FX rates from Bacen API
│                                      # Key concepts:
│                                      # - httpx.Client (context manager)
│                                      # - Pydantic validation of API response
│                                      # - Error handling for weekends/holidays
│
├── synthetic/
│   ├── generator.py                   # Generates fake sales/customers/products
│   │                                  # Key concepts:
│   │                                  # - Faker for random data
│   │                                  # - pandas DataFrames
│   │                                  # - Parquet file format
│   │                                  # - Idempotent writes (overwrite, not append)
│   │
│   └── seed_data.py                   # Static catalogs
│                                      # Product categories, customer names, etc.
│                                      # Used by generator.py
│
└── common/
    ├── s3.py                          # Helper functions for S3 operations
    │                                  # Key concepts:
    │                                  # - boto3 for AWS SDK
    │                                  # - Writing Parquet to S3
    │                                  # - Date-based partitioning
    │
    └── loader.py                      # Loads Parquet from S3 → Postgres Bronze
                                       # Key concepts:
                                       # - SQLAlchemy for database connections
                                       # - Idempotent upsert (same date = overwrite)
                                       # - Adding _ingested_at timestamp
```

### How ingestion works

1. **Bacen fetcher** runs: HTTP GET → Parquet to S3 (`bronze/bacen_ptax/ingestion_date=YYYY-MM-DD/`)
2. **Synthetic generator** runs: creates fake data → Parquet to S3 (`bronze/internal_*/ingestion_date=YYYY-MM-DD/`)
3. **Loader** runs: reads all Parquets from S3 → inserts to Postgres Bronze tables

All called by `run_pipeline.py` in sequence.

---

## `/dbt` — Transformations (Bronze → Silver → Gold)

```
dbt/
├── dbt_project.yml                    # dbt project config
│                                      # Sets project name, profile, model paths, etc.
│
├── profiles.yml.example               # Template for local database connection
│                                      # Copy to profiles.yml and fill with credentials
│
├── models/
│   ├── staging/                       # Silver layer (cleaned, typed, conformed)
│   │   ├── stg_bacen_ptax.sql        # FX rates (cleaned, forward-filled)
│   │   ├── stg_bacen_ptax.yml        # Schema, tests, column descriptions
│   │   │
│   │   ├── stg_sales.sql             # Sales orders (typed, deduplicated)
│   │   ├── stg_sales.yml
│   │   │
│   │   ├── stg_customers.sql         # Customer dimensions (typed)
│   │   ├── stg_customers.yml
│   │   │
│   │   ├── stg_products.sql          # Product dimensions (typed, with price_tier)
│   │   └── stg_products.yml
│   │
│   │                                  # Key dbt concepts here:
│   │                                  # - {{ source() }} to read Bronze
│   │                                  # - {{ ref() }} to reference other models
│   │                                  # - CTEs (Common Table Expressions) for clarity
│   │                                  # - Tests in .yml files (not_null, unique, etc.)
│   │                                  # - Column descriptions for documentation
│   │
│   └── marts/                         # Gold layer (business-ready aggregates)
│       ├── mart_sales.sql            # Daily revenue by category (with FX conversion)
│       │                             # Key concepts:
│       │                             # - Joining multiple Silver tables
│       │                             # - Window functions for rolling 7d averages
│       │                             # - jinja templating in dbt
│       │
│       └── mart_sales.yml            # Schema, tests, documentation
│
├── tests/
│   └── singular/                      # Custom SQL tests
│       └── assert_no_negative_revenue.sql
│                                      # Tests that revenue in Gold is always >= 0
│
├── seeds/                             # Reference/lookup data
│   └── (empty for v1.1, used in v2 for category mappings)
│
└── macros/
    └── (empty for v1.1, can add helpers in v2)
```

### How dbt works in the pipeline

```
run_pipeline.py calls: dbt build
  ↓
dbt build = dbt run + dbt test
  ↓
dbt run:
  - Reads Bronze tables (via {{ source() }})
  - Transforms through Silver models
  - Creates Silver tables in postgres.silver schema
  - Transforms through Gold models
  - Creates Gold tables in postgres.gold schema
  ↓
dbt test:
  - Runs all tests in .yml files
  - Runs all singular tests in /tests
  - Fails build if any test fails (catches data quality issues early)
```

### Key dbt concepts you'll encounter

- **`{{ source() }}`** — reads from Bronze layer; defined in `schema.yml` with sources
- **`{{ ref() }}`** — references other dbt models; builds the DAG
- **CTEs (WITH clauses)** — organize SQL logic step-by-step
- **Tests** — `not_null`, `unique`, `relationships`, custom SQL assertions
- **Jinja** — template variables in SQL (e.g., `{{ env_var('KEY') }}`)
- **Materializations** — v1.1 uses `table` (rebuild each run); v2 uses `incremental`

---

## `/dashboard` — Streamlit BI

```
dashboard/
└── app.py                             # Streamlit dashboard application
                                       # Key concepts:
                                       # - Streamlit for web dashboard
                                       # - Connecting to Postgres from Python
                                       # - Plotting with Streamlit/Plotly
                                       # - Interactive elements (filters, refresh)
                                       #
                                       # Displays:
                                       # 1. Daily revenue line chart (BRL + USD)
                                       # 2. Category breakdown (bar chart)
                                       # 3. 7-day rolling average overlay
```

### How to run

```bash
streamlit run dashboard/app.py
# Opens browser to http://localhost:8501
```

---

## `/docs` — Documentation & Decisions

```
docs/
├── 01_discovery_report.md             # What the project is, why it's portfolio-grade
│
├── 01_discovery_report_addendum.md    # How v1.1 differs from original v1 plan
│
├── 02_prd_for_claude_code.md          # Old v1 PRD (historical, don't use)
│
├── 02_prd_v11.md                      # **ACTIVE** v1.1 PRD — the spec Claude Code reads
│
├── 03_time_estimate.md                # Old v1 time estimate (historical)
│
├── 03_time_estimate_v11.md            # **ACTIVE** v1.1 time estimate with tracking template
│
├── 06_roadmap_v1_to_v2.md             # Explicit path from v1.1 to v2 in 3 phases
│
├── decisions/                         # Architecture Decision Records
│   ├── README.md                      # Index of all 11 ADRs with reading order
│   ├── TEMPLATE.md                    # Template for writing new ADRs
│   │
│   ├── 0001-use-medallion-architecture.md
│   ├── 0002-meli-as-primary-source.md (Superseded by 0009)
│   ├── 0003-synthetic-internal-data.md
│   ├── 0004-prefect-over-github-actions.md (Superseded by 0010)
│   ├── 0005-metabase-over-streamlit.md (Superseded by 0011)
│   ├── 0006-defer-dbt-ci-to-v2.md
│   ├── 0007-security-baseline.md
│   ├── 0008-claude-md-human-edited-only.md
│   ├── 0009-defer-meli-to-v2.md (Supersedes 0002)
│   ├── 0010-defer-prefect-to-v2.md (Supersedes 0004)
│   └── 0011-streamlit-over-metabase-v11.md (Supersedes 0005)
│
└── architecture.png                   # (Will create after M1)
                                       # Diagram of: S3 → Postgres → dbt → Streamlit
```

### What to read when

**Before starting Milestone 1:** Read `02_prd_v11.md` completely.

**While building:** Reference specific milestones in the PRD. Read the ADRs when curious about "why did we choose X?"

**During v2 planning:** Read `06_roadmap_v1_to_v2.md` to pick the next phase.

---

## `/security` — Security Setup

```
security/
├── README.md                          # Step-by-step setup for IAM + gitleaks
│                                      # Instructions for:
│                                      # 1. Creating scoped S3 IAM user
│                                      # 2. Installing gitleaks locally
│                                      # 3. Running pre-commit hooks
│                                      # 4. What to do if a secret leaks
│
└── iam-policy-s3.json                 # JSON policy template
                                       # Copy to AWS, replace bucket name
                                       # Grants: ListBucket, GetObject, PutObject
                                       # Scope: only your S3 bucket, nothing else
```

---

## Root Configuration Files

### `.env.example`

```bash
# Database
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key_here

# S3
AWS_ACCESS_KEY_ID=your_aws_key_id
AWS_SECRET_ACCESS_KEY=your_aws_secret_key
S3_BUCKET=your-bucket-name

# (No MELI, Prefect, etc. — those are v2)
```

**Never commit `.env`.** The `.example` file shows the shape; real values stay local only.

### `.gitignore`

```
.env
.venv/
__pycache__/
*.pyc
.DS_Store
dbt/target/
dbt/dbt_packages/
.dbt/
logs/
```

### `pyproject.toml`

```toml
[project]
name = "dw-mercadolivre"
version = "0.1.0"
description = "Daily Data Warehouse with Medallion architecture"

[project.dependencies]
# Ingestion
httpx = "^0.27"
pandas = "^2.1"
faker = "^24"
boto3 = "^1.34"
pydantic = "^2.5"
sqlalchemy = "^2.0"
psycopg2-binary = "^2.9"

# dbt
dbt-core = "^1.7"
dbt-postgres = "^1.7"

# Dashboard
streamlit = "^1.28"
plotly = "^5.18"

# Utilities
python-dotenv = "^1.0"

[tool.uv]
# (uv automatically manages Python version)
```

### `CLAUDE.md`

```markdown
# Working Agreement for Claude Code on dw-mercadolivre v1.1

## Project

The human is learning Python and SQL. dbt, S3, Streamlit are new. Goal: ship v1.1 (8 milestones, 39-68 hours), understand every line.

## Stack

- Supabase Postgres (Bronze/Silver/Gold schemas)
- AWS S3 (ingestion Parquet landing)
- Python 3.13+ (httpx, pandas, pydantic, sqlalchemy, faker)
- dbt-core + dbt-postgres
- Streamlit

## Spec

Canonical spec: `docs/02_prd_v11.md`. Read fully before any code.
Decisions: `docs/decisions/` (11 ADRs with full reasoning).
Estimates: `docs/03_time_estimate_v11.md` (track actuals as you go).

## Teaching Protocol

**You write code.** Human reads with explanations.

1. **Narrate briefly before code** — "Now writing X to do Y. New concept here: Z."
2. **Explain language concepts** when introduced (list comp, context manager, CTE, window func, etc.).
3. **One concept per code block** when possible.
4. **Repeat patterns explicitly** — "Same context manager as the S3 client."
5. **Active recall at inflection points only** — First S3 call, first dbt model, first SQL join. Ask human to predict before running.
6. **No exercises.** Human keeps moving, asks when curious.
7. **After code: one question** — usually "want to run it?" or at inflection points, a prediction.

## Guardrails

- One dbt model per response (if asked for "Silver layer")
- Never silently install dependencies — propose + wait
- Never use Out of Scope items (§10 of PRD)
- When uncertain about API/library, verify docs not guess
- Flag anything touching secrets/IAM/auth — don't proceed silently

## Out of Scope (v2)

Mercado Livre API, Prefect, Metabase, dbt CI, incremental models, SCD2, multi-env.

If asked, respond: "That's in v2. Keep for later or add to v1.1?"

## Decision Log

When making a logged-category decision (tool choice, architecture, scope), say "I'll log this as ADR-NNNN" and write to `docs/decisions/NNNN-kebab-case.md` using TEMPLATE.md.

## Security

Never skip gitleaks. Narrate when touching secrets/IAM/auth. No AmazonS3FullAccess. Use SUPABASE_SERVICE_ROLE_KEY not SUPABASE_KEY.

## Token Budget

Avoid restating instructions, long preambles, recapping state every turn. Be terse before/after code.

## CLAUDE.md Edits

Human-edited only. Propose diffs, wait for application.
```

### `run_pipeline.py`

```python
#!/usr/bin/env python3
"""
Single entrypoint for the dw-mercadolivre pipeline.

Runs in sequence:
1. Generate synthetic sales data → S3
2. Fetch Bacen PTAX FX rates → S3
3. Load S3 Parquets → Postgres Bronze
4. Run dbt build (transform Bronze → Silver → Gold, run tests)
5. Print summary

Usage:
    python run_pipeline.py
"""

# TBD — written during Milestone 8
```

---

## Directory Summary Table

| Path | Purpose | Owner | Notes |
|---|---|---|---|
| `/ingestion` | Data fetching & loading | `ingestion/*.py` written by Claude Code | Bronze layer creation |
| `/dbt` | SQL transformations | `models/*.sql` written by Claude Code | Silver & Gold creation |
| `/dashboard` | BI visualization | `dashboard/app.py` written by Claude Code | Interactive charts |
| `/docs` | Specs, decisions, plans | Human-created + Claude Code for decisions | Study material |
| `/security` | Auth & secrets setup | Human-executed per README | One-time setup |
| Root configs | Environment & project | Human creates from templates | Never committed (`.env`) |

---

## Execution Flow

When you run `python run_pipeline.py`:

```
run_pipeline.py
  ├─ ingestion.synthetic.generator.main()
  │   └─ S3: bronze/internal_sales/ingestion_date=YYYY-MM-DD/sales.parquet
  │   └─ S3: bronze/internal_customers/ingestion_date=YYYY-MM-DD/customers.parquet
  │   └─ S3: bronze/internal_products/ingestion_date=YYYY-MM-DD/products.parquet
  │
  ├─ ingestion.bacen.fetch.main()
  │   └─ S3: bronze/bacen_ptax/ingestion_date=YYYY-MM-DD/ptax.parquet
  │
  ├─ ingestion.common.loader.main()
  │   └─ Postgres Bronze: bronze.internal_sales, bronze.internal_customers, etc.
  │
  ├─ dbt build
  │   ├─ Create Silver: stg_bacen_ptax, stg_sales, stg_customers, stg_products
  │   ├─ Test Silver: not_null, unique, relationships
  │   ├─ Create Gold: mart_sales
  │   ├─ Test Gold: non-negative revenue
  │   └─ Generate docs (viewable at target/compiled/index.html)
  │
  └─ Print: "Pipeline complete. X rows loaded. All tests passed."
```

To view the dashboard:

```
streamlit run dashboard/app.py
```

---

## What's NOT here yet (v2)

- `ingestion/meli/` — Mercado Livre API fetcher
- `flows/` — Prefect orchestration
- `metabase/` — Docker Compose setup
- `tests/` — Python unit tests

These are documented in `docs/06_roadmap_v1_to_v2.md`.

---

## Ready to create this structure?

You now have the full map. When you create the repo on GitHub, this is the exact shape to build out. Don't overthink it — start with Milestone 1, and Claude Code will write the files as you go. You don't need to create empty directories; just clone the repo and follow the PRD.

Next step: **Create the GitHub repo, then start Milestone 1 with Claude Code.**
