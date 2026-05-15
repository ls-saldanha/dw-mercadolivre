# M3 — Bacen PTAX Fetcher

---

## [2026-05-15] Checkpoint: Fetcher written

*No commit yet — written in current session, pre-run.*

**What we built:** `ingestion/bacen/fetch.py` — fetches the USD/BRL PTAX rate from the Bacen OLINDA API, validates the response with Pydantic, and writes a one-row Parquet file to S3. Handles weekends and holidays by walking back up to 7 days to find the most recent business-day rate.

**Files touched:**
- `ingestion/bacen/__init__.py` — package marker
- `ingestion/bacen/fetch.py` — fetcher: `_fetch_for_date()`, `fetch_latest_rate()`, `run()`
- `pyproject.toml` — added `httpx` dependency
- `uv.lock` — updated

**New concepts introduced:**
- *`httpx` context manager* — `with httpx.Client(timeout=30) as client:` guarantees the HTTP connection is cleaned up when the block exits, even on error. Same `with` / context manager pattern as `with open("file.txt") as f:` or the boto3 S3 client setup
- *Pydantic for API response validation* — instead of indexing into a raw dict (`payload["value"][0]["cotacaoCompra"]`) and hoping the key exists, we define `_PtaxRate(BaseModel)` and do `_PtaxRate(**payload["value"][0])`. If a field is missing or the wrong type, Pydantic raises immediately — not three steps later
- *Returning `None` as a sentinel* — `_fetch_for_date()` returns `None` when the API returns an empty list (weekend / holiday). The caller checks for `None` before using the result. Simple alternative to raising an exception for an expected case
- *`timedelta` arithmetic* — `reference_date - timedelta(days=days_back)` walks a date backwards one day at a time. `timedelta` is Python's way of representing a duration (days, seconds, etc.) that can be added to or subtracted from a `date`

**Patterns reused:**
- Same `write_parquet()` call from `ingestion/common/s3.py` — same as synthetic generator
- Same `_ingested_at` column added on every Bronze write — consistent with `bronze.*` schema convention
- Same `ingestion_date=YYYY-MM-DD` S3 partition key pattern

**What broke and how we fixed it:** Not yet run — no breakage documented.

**Decisions logged:** None new.

**Next step:** Run `uv run python -m ingestion.bacen.fetch` against real credentials and verify S3 write.

---

## Status: in progress

Currently working on: running the fetcher for the first time against the live Bacen endpoint.

Outstanding for M3 acceptance:
- [ ] PTAX fetch succeeds for today's date
- [ ] Weekend/holiday case handled (lookback finds most recent business-day rate)
- [ ] File lands in S3 at `bronze/bacen_ptax/ingestion_date=YYYY-MM-DD/ptax.parquet`
- [ ] Re-running same day is idempotent (overwrites, no duplicate rows)
