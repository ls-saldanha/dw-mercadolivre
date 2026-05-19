# Milestone 4 — Bronze Loader

## 2026-05-19 Checkpoint: S3 → Postgres Bronze

**What we built:** `ingestion/common/loader.py` reads today's Parquet files from S3 and loads them into four Postgres `bronze` tables — `internal_sales`, `internal_customers`, `internal_products`, and `bacen_ptax`. Running it twice on the same day produces the same row counts (idempotent).

**Files touched:**
- `ingestion/common/loader.py` — new file, the Bronze loader
- `ingestion/common/s3.py` — added `list_keys(prefix)` for S3 pagination
- `pyproject.toml` — added `sqlalchemy` dependency

**New concepts introduced:**
- **SQLAlchemy engine** — a connection factory (`create_engine(url)`) that opens DB connections on demand. URL format: `postgresql+psycopg2://user:password@host:5432/db`.
- **`df.to_sql()`** — pandas method that writes a DataFrame to a SQL table. `if_exists='append'` adds rows without replacing the table; `schema=` targets a specific Postgres schema.
- **DELETE + INSERT idempotency** — every row gets an `ingestion_date DATE` column. Before inserting, `DELETE WHERE ingestion_date = today` clears the day's previous load. Re-running never duplicates rows.
- **S3 paginator** — `list_objects_v2` returns at most 1,000 keys per call. boto3's `get_paginator` handles multi-page results automatically; `list_keys()` always returns all files under a prefix.

**Patterns reused:**
- Same `_client()` factory pattern as `s3.py` — one function that builds the boto3/SQLAlchemy client from env vars.
- Same `run(ingestion_date)` entry-point convention as `bacen/fetch.py` and `synthetic/generator.py`.

**Active recall moment:** Asked to predict what `bronze.internal_products` would contain after the first run, and what a second run would do. Correct: 50 rows after run 1; still 50 rows after run 2 (DELETE replaced the previous load, no duplicates).

**Why not MERGE?** Bronze is raw landing — Silver (dbt) handles deduplication. MERGE requires a key assumption about the data before it's been cleaned. DELETE + INSERT treats Bronze as "today's arrival" without any uniqueness constraints.

**Verified:** Row counts in Postgres — 200 sales, 200 customers, 50 products, 1 PTAX rate. Idempotency confirmed by running loader twice.

**Next step:** M5 — four dbt Silver staging models (`stg_internal_sales`, `stg_internal_customers`, `stg_internal_products`, `stg_bacen_ptax`).
