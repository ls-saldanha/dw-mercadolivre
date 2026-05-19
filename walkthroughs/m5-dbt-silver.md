# Milestone 5 — dbt Silver

## 2026-05-19 Checkpoint: Four staging models, 26/26 tests passing

**What we built:** Four dbt views in the `silver` schema that clean, type, and deduplicate the Bronze tables. dbt runs SQL transformations and then tests every model — if a test fails, the pipeline stops before Gold is ever touched.

**Files touched:**
- `dbt/dbt_project.yml` — project config; staging materialized as views, marts as tables
- `dbt/profiles.yml` — Supabase connection via `SUPABASE_DB_PASSWORD` env var (gitignored)
- `dbt/macros/generate_schema_name.sql` — overrides dbt default so `+schema: silver` produces exactly `silver`, not `public_silver`
- `dbt/models/staging/sources.yml` — declares the four Bronze source tables
- `dbt/models/staging/stg_internal_sales.sql`
- `dbt/models/staging/stg_internal_customers.sql`
- `dbt/models/staging/stg_internal_products.sql`
- `dbt/models/staging/stg_bacen_ptax.sql`
- `dbt/models/staging/schema.yml` — 22 data tests across all four models

**New concepts introduced:**
- **dbt `source()`** — `{{ source('bronze', 'internal_sales') }}` resolves to the real table at runtime and registers lineage in dbt's DAG. dbt knows this model depends on that Bronze table.
- **`dbt build`** — runs `dbt run` + `dbt test` in one command. A test failure halts everything; Gold is never updated with bad data.
- **CTEs as layers** — each model follows the same pattern: `source` → `typed` → `deduplicated` → final select. One concern per CTE.
- **`row_number() over (partition by ... order by ...)`** — window function that assigns a rank to each row within a group. Filtering `where rn = 1` keeps the latest row per primary key. This is the standard SQL deduplication pattern.
- **`ntile(3)` window function** — divides all rows into 3 equal buckets ordered by a column. Used in `stg_internal_products` to assign `price_tier` based on actual data distribution (quantile), not hardcoded thresholds.
- **`accepted_values` test** — dbt generates a query that returns rows where the column value is NOT in the allowed list. Any result = test failure.
- **`relationships` test** — verifies every `customer_id` in sales exists in the customers model. Foreign key integrity without a database constraint.
- **`generate_schema_name` macro** — Jinja macro that overrides dbt's default schema naming. Without it, `+schema: silver` would produce `public_silver`.

**Patterns reused:**
- Same `source` → `typed` → `deduplicated` CTE structure in all four models.
- Same `row_number() over (partition by pk order by ingestion_date desc)` deduplication in all four models.

**What broke and how we fixed it:** dbt 1.9+ deprecated top-level arguments on generic tests (`relationships`, `accepted_values`). Fixed by nesting them under `arguments:` in `schema.yml`.

**Next step:** M6 — `mart_sales` Gold model. Joins all four Silver models, computes `revenue_usd` via PTAX bid rate, and adds a 7-day rolling revenue window function.
