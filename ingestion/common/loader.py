"""
loader.py — reads today's S3 Parquet files and loads them into Postgres Bronze tables.

Each load is idempotent: rows for the given ingestion_date are deleted before
inserting, so re-running the same day never duplicates data.

Usage:
    python -m ingestion.common.loader
    python -m ingestion.common.loader --date 2026-05-19
"""

import argparse
import os
from datetime import date
from urllib.parse import urlparse

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

from ingestion.common.s3 import list_keys, read_parquet

# S3 prefix → Postgres table (schema.table)
SOURCES: dict[str, str] = {
    "bronze/internal_sales": "bronze.internal_sales",
    "bronze/internal_customers": "bronze.internal_customers",
    "bronze/internal_products": "bronze.internal_products",
    "bronze/bacen_ptax": "bronze.bacen_ptax",
}

# DDL for all four Bronze tables.
# ingestion_date lets us DELETE the day's rows before re-inserting (idempotency).
_CREATE_TABLES_SQL = """
CREATE SCHEMA IF NOT EXISTS bronze;

CREATE TABLE IF NOT EXISTS bronze.internal_sales (
    order_id          TEXT,
    customer_id       TEXT,
    product_id        TEXT,
    quantity          INTEGER,
    unit_price_brl    NUMERIC(10, 2),
    total_price_brl   NUMERIC(10, 2),
    ordered_at        TIMESTAMPTZ,
    ingestion_date    DATE,
    _ingested_at      TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS bronze.internal_customers (
    customer_id    TEXT,
    name           TEXT,
    email          TEXT,
    city           TEXT,
    state          TEXT,
    created_at     TIMESTAMPTZ,
    ingestion_date DATE,
    _ingested_at   TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS bronze.internal_products (
    product_id     TEXT,
    name           TEXT,
    category       TEXT,
    unit_price_brl NUMERIC(10, 2),
    ingestion_date DATE,
    _ingested_at   TIMESTAMPTZ
);

CREATE TABLE IF NOT EXISTS bronze.bacen_ptax (
    cotacao_date      TEXT,
    bid_rate          NUMERIC(10, 4),
    ask_rate          NUMERIC(10, 4),
    source_timestamp  TEXT,
    ingestion_date    DATE,
    _ingested_at      TIMESTAMPTZ
);
"""


def _build_db_url() -> str:
    """Construct a PostgreSQL connection URL from environment variables.

    Supabase's REST URL (SUPABASE_URL) follows the pattern:
        https://<project-ref>.supabase.co
    The direct DB host is:
        db.<project-ref>.supabase.co
    """
    supabase_url = os.environ["SUPABASE_URL"]
    password = os.environ["SUPABASE_DB_PASSWORD"]
    host = urlparse(supabase_url).hostname  # e.g. abcdef.supabase.co
    project_ref = host.split(".")[0]        # e.g. abcdef
    db_host = f"db.{project_ref}.supabase.co"
    return f"postgresql+psycopg2://postgres:{password}@{db_host}:5432/postgres"


def _engine():
    """Return a SQLAlchemy engine connected to Supabase."""
    return create_engine(_build_db_url())


def _ensure_tables(engine) -> None:
    """Create the bronze schema and tables if they don't already exist."""
    with engine.begin() as conn:
        conn.execute(text(_CREATE_TABLES_SQL))


def _load_table(
    engine,
    s3_prefix: str,
    table: str,
    ingestion_date: date,
) -> None:
    """Load one Bronze table from today's S3 partition.

    Steps:
    1. List all Parquet files under the partition prefix.
    2. Read and concatenate them into one DataFrame.
    3. Stamp ingestion_date and _ingested_at columns.
    4. Delete any existing rows for this ingestion_date (idempotency).
    5. Append the new rows.
    """
    date_str = ingestion_date.isoformat()
    prefix = f"{s3_prefix}/ingestion_date={date_str}/"
    keys = list_keys(prefix)

    if not keys:
        print(f"  {table}: no files found at s3://{os.environ['S3_BUCKET']}/{prefix} — skipping")
        return

    frames = [read_parquet(key) for key in keys]
    df = pd.concat(frames, ignore_index=True)

    df["ingestion_date"] = ingestion_date
    if "_ingested_at" not in df.columns:
        df["_ingested_at"] = pd.Timestamp.now(tz="UTC")

    schema, tbl = table.split(".")
    with engine.begin() as conn:
        conn.execute(
            text(f"DELETE FROM {table} WHERE ingestion_date = :d"),
            {"d": date_str},
        )

    df.to_sql(tbl, engine, schema=schema, if_exists="append", index=False)
    print(f"  {table}: loaded {len(df)} rows for {date_str}")


def run(ingestion_date: date | None = None) -> None:
    """Load all Bronze tables for the given date. Defaults to today."""
    if ingestion_date is None:
        ingestion_date = date.today()

    print(f"\nLoading Bronze tables for {ingestion_date.isoformat()}...")
    engine = _engine()
    _ensure_tables(engine)

    for s3_prefix, table in SOURCES.items():
        _load_table(engine, s3_prefix, table, ingestion_date)

    print("Bronze load complete.")


if __name__ == "__main__":
    load_dotenv()

    parser = argparse.ArgumentParser()
    parser.add_argument("--date", help="YYYY-MM-DD (default: today)", default=None)
    args = parser.parse_args()

    target_date = date.fromisoformat(args.date) if args.date else None
    run(target_date)
