> **Note:** This walkthrough was backfilled after the protocol was added to CLAUDE.md. Fields marked `[inferred]` were reconstructed from repo state rather than recorded at the time. Commits and debugging notes referenced inline are real. Future walkthroughs will be written at checkpoint time.

# M2 — Synthetic Data Generator

---

## [2026-05-15] Checkpoint: Generator and S3 helpers — M2 complete

*Commit `b525887` — "feat: Milestone 2 — synthetic data generator"*

**What we built:** Three-table synthetic generator (200 sales + 200 customers + 50 products per day) that writes Parquet files to S3 bronze partitions. Fixed-per-date seeds make runs reproducible. Also extracted the `ingestion/common/s3.py` write/read helpers that every future ingestion module (Bacen, eventually MeLi) will reuse.

**Files touched:**
- `ingestion/common/s3.py` — `write_parquet()` and `read_parquet()` helpers wrapping boto3
- `ingestion/synthetic/__init__.py` — package marker
- `ingestion/synthetic/generator.py` — main generator: builds DataFrames using Faker and pandas, writes to S3
- `ingestion/synthetic/seed_data.py` — fixed category, name, and product seed lists
- `pyproject.toml` — added `faker` dependency
- `uv.lock` — updated

**New concepts introduced:** [inferred]
- *Faker library* — generates realistic fake data (names, addresses, prices). `Faker()` creates a generator; methods like `.name()`, `.date_this_year()`, `.pyfloat()` produce values on demand
- *pandas DataFrame* — a table in memory, like a spreadsheet. You build one from a list of dicts, then call methods on it (`.to_parquet()`, `.merge()`, `.groupby()`)
- *Parquet format* — binary columnar file format. Compared to CSV: ~10× smaller, typed (no guessing if "1.5" is a float or a string), and faster to read because you can skip columns you don't need. The standard format for data lakes
- *S3 partitioning by date* — storing files at `bronze/{source}/ingestion_date=YYYY-MM-DD/` lets tools like Athena and dbt filter by date without scanning all files. The `ingestion_date=` prefix follows the Hive partition convention — tools recognise it automatically
- *Idempotent writes* — re-running the same day's ingestion overwrites the same S3 key rather than appending. This means "run it again" is safe and produces the same result
- *Fixed seeds* — passing `random.seed(date_int)` means the same date always produces the same fake data. Useful for testing: you can re-run and compare

**Patterns reused:** [inferred]
- Same `boto3` client setup from `smoke_test.py` — now extracted into `s3.py` so no module needs to touch boto3 directly
- Same `os.environ[]` credential pattern for `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `S3_BUCKET`

**What broke and how we fixed it:** No specific breakage documented for M2.

**Decisions logged:** None new — M2 implements decisions already captured in ADR-0003 (synthetic internal data).

**Next step:** Move to M3 — Bacen PTAX fetcher.

---

## Milestone Complete

M2 closed at commit `b525887` on 2026-05-15. Acceptance criterion met: three Parquet files written to S3. Re-running same day overwrites idempotently.

The `ingestion/common/s3.py` extraction is the lasting structural contribution of M2 — every subsequent ingestion module calls `write_parquet()` instead of touching boto3 directly. One place to change if we ever swap storage backends.

Next: [m3-bacen.md](m3-bacen.md)
