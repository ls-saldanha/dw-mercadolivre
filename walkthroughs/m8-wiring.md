# Milestone 8 — Wire-up and Docs

## 2026-05-19 Milestone close: v1.1 complete

**What we built:** `run_pipeline.py` wired up all four steps into one command. README rewritten as a portfolio-ready document. Full end-to-end run confirmed: 32/32 dbt tests passing.

**Files touched:**
- `run_pipeline.py` — fully implemented (was a skeleton)
- `README.md` — rewritten with pitch, ASCII architecture diagram, stack table, setup instructions, data model reference

**New concept introduced:**
- **`subprocess.run()`** — how Python calls an external program (dbt) from within a script. `check=True` means if dbt exits with a non-zero code (tests fail), the pipeline raises an exception and stops. `Path(sys.executable).parent / "dbt"` finds the dbt binary in the same virtual environment as Python, so it always uses the right version.

**End-to-end verified:**
```
[1/4] Synthetic data → S3     200 sales, 200 customers, 50 products
[2/4] Bacen PTAX → S3         bid=5.0087 ask=5.0093
[3/4] S3 Parquets → Bronze    4 tables loaded
[4/4] dbt build               32/32 PASS, 0 WARN, 0 ERROR
```

## Milestone Complete — v1.1

All eight milestones shipped:

| Milestone | Delivered |
|---|---|
| M1 Foundation | Supabase schemas, S3 bucket, gitleaks pre-commit, smoke test green |
| M2 Synthetic generator | Parquet to S3, idempotent, 200 sales/day |
| M3 Bacen fetcher | PTAX from Bacen OLINDA API, weekend/holiday handled |
| M4 Bronze loader | S3 → Postgres, DELETE+INSERT idempotency, all 4 tables |
| M5 dbt Silver | 4 staging views, 22 generic tests, deduplication, price_tier via ntile(3) |
| M6 dbt Gold | mart_sales — BRL/USD revenue, 7-day rolling, 5 tests |
| M7 Dashboard | Streamlit, 3 Plotly charts, st.cache_data |
| M8 Wire-up | run_pipeline.py end-to-end, portfolio README |

**What comes next (v2):** Mercado Livre API integration, Prefect orchestration, Metabase BI layer — see `docs/ROADMAP.md`.
