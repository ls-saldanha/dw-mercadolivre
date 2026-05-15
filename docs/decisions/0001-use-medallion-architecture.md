# ADR-0001: Use Medallion architecture (Bronze → Silver → Gold)

**Status:** Accepted
**Date:** 2026-05-14

## Context

The project needs a layered data architecture that separates raw ingestion from transformation and from business-level aggregation. The human is learning data engineering concepts alongside the project, so the architecture needs to be legible and commonly taught.

## Decision

**Use the Medallion architecture with three layers stored in Postgres schemas:**

- **Bronze** (`bronze` schema + S3 Parquet): raw, append-only data as it arrived from the source. No transformations. One extra column `_ingested_at` added on load.
- **Silver** (`silver` schema, dbt models): typed, deduplicated, conformed. One model per source entity. Named `stg_{source}_{entity}`.
- **Gold** (`gold` schema, dbt models): business-level aggregations. Named `mart_{domain}`.

S3 acts as the Bronze landing zone before Postgres. Layout: `s3://{bucket}/bronze/{source}/ingestion_date=YYYY-MM-DD/`.

## Alternatives considered

- **Two-layer (raw + presentation)** — simpler, but conflates cleaning with business logic. Harder to debug which layer introduced a problem.
- **OBT (one big table)** — common in small projects, but not teachable as a pattern and collapses as data sources grow.
- **Delta Lake / Iceberg on S3 only** — no Postgres needed, but adds lakehouse concepts the human doesn't need yet.

## Consequences

- Each layer has a clear, single responsibility — easy to reason about and explain
- Re-running ingestion on the same day is idempotent: Bronze overwrites the partition, Silver/Gold rebuild from it
- Three Postgres schemas need to be created in Supabase before first run
- dbt naturally models the Silver→Gold transition; Bronze loading is handled by Python
