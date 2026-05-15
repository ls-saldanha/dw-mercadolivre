# Time Estimate — `dw-mercadolivre` v1.1

**Supersedes:** `03_time_estimate.md` (the v1 estimate)

**What changed:** v1 estimated 41–75 hours assuming the human would write SQL and Python fluently. v1.1 estimates similar total hours but spent very differently. Less time on tools that were cut (Prefect, Metabase, MELI OAuth). More time on understanding code that Claude Code writes.

## The honest disclaimer (again)

These are ranges, not predictions. Software estimates from someone who isn't doing the work are notoriously unreliable. Track your actuals as you go — the gap between estimate and actual is the most useful number on this page.

## Summary

| Phase | Low | High | Notes |
|---|---|---|---|
| M1 — Foundation | 4h | 7h | Account signups, smoke test, security setup |
| M2 — Synthetic generator | 4h | 7h | Python concepts: modules, Faker, pandas |
| M3 — Bacen fetcher | 2h | 4h | HTTP, Pydantic, context managers |
| M4 — S3 → Postgres loader | 3h | 5h | SQLAlchemy, idempotency |
| M5 — dbt setup + Silver | 6h | 10h | dbt concepts: refs, configs, tests, CTEs |
| M6 — dbt Gold mart | 4h | 7h | SQL joins, window functions, jinja |
| M7 — Streamlit dashboard | 3h | 5h | Plotting, DB connections in Python |
| M8 — Wire-up + docs + post | 4h | 7h | Including ~2h for the blog post |
| **v1.1 subtotal** | **30h** | **52h** | |
| Buffer (+30% for learning-while-building) | +9h | +16h | |
| **Realistic v1.1 total** | **~39h** | **~68h** | |

At 2 hours/day, that's **4–8 weeks**. At 4 hours per weekend day, **5–8 weekends**. Doable.

**Compared to v1:** v1 was 41–75 hours, v1.1 is 39–68 hours. Similar magnitude, very different makeup. v1 had more tooling to learn (Prefect, OAuth, Docker). v1.1 has less tooling but slower per-line pace because everything is being learned, not just typed.

## Where the hours go in v1.1 vs v1

| Phase | v1 hours | v1.1 hours | Why the change |
|---|---|---|---|
| Foundation | 3–6h | 4–7h | Slightly slower without prior Python comfort |
| Ingestion (all sources) | 8–14h | 9–16h | Slower pace, but only 2 sources instead of 3 (no MELI) |
| dbt Silver | 5–9h | 6–10h | Same model count, deeper explanations |
| dbt Gold | 6–11h | 4–7h | Only 1 mart instead of 3 |
| Orchestration | 4–7h | 0h | Removed (Prefect → v2) |
| BI | 3–6h | 3–5h | Streamlit is simpler than Metabase |
| Documentation | 4–7h | 4–7h | Same |

The big wins are removing Prefect (-4 to -7h) and cutting Gold from 3 marts to 1 (-2 to -4h). The pace slowdown adds time back, but net we're at roughly the same total.

## Subtask breakdown by milestone

### M1 — Foundation (4–7h)

| Subtask | Low | High |
|---|---|---|
| Repo init, virtualenv, pyproject, .gitignore | 30m | 1h |
| Supabase project, schemas, connection string | 30m | 1h |
| AWS S3 bucket + IAM user with scoped policy | 1h | 2h |
| Install `gitleaks` + pre-commit hooks | 30m | 1h |
| Smoke test script | 1.5h | 2h |

**Variance drivers:** AWS IAM is the unknown. If you've never written an IAM policy, budget high. Claude Code will explain it as it goes.

### M2 — Synthetic generator (4–7h)

| Subtask | Low | High |
|---|---|---|
| Static seed data (catalogs, names) | 1h | 1.5h |
| Generator function (sales/customers/products) | 1.5h | 3h |
| Parquet writing to S3 | 1h | 1.5h |
| Verification + cleanup | 30m | 1h |

**Teaching load:** This is where you'll learn Python data idioms — DataFrames, list/dict comprehensions, context managers, function arguments. Expect concept-density.

### M3 — Bacen fetcher (2–4h)

| Subtask | Low | High |
|---|---|---|
| HTTP client + endpoint call | 30m | 1h |
| Pydantic response models | 45m | 1.5h |
| Weekend/holiday handling | 30m | 45m |
| S3 write + verification | 30m | 45m |

**Teaching load:** HTTP basics, JSON, Pydantic validation. Concept-light compared to M2.

### M4 — S3 → Postgres loader (3–5h)

| Subtask | Low | High |
|---|---|---|
| SQLAlchemy connection + table creation | 1h | 1.5h |
| Idempotent upsert logic | 1h | 2h |
| Re-run safety verification | 1h | 1.5h |

**Teaching load:** SQLAlchemy ORM-vs-Core, what idempotency means.

### M5 — dbt setup + Silver models (6–10h)

| Subtask | Low | High |
|---|---|---|
| dbt project init, profiles, debug | 1h | 2h |
| First Silver model (`stg_bacen_ptax`) — deep teach | 2h | 3h |
| Remaining 3 Silver models | 2h | 3.5h |
| Schema YAMLs with tests | 1h | 1.5h |

**Variance drivers:** This is the conceptual hump of the project. The first dbt model is where the mental model clicks (or doesn't). Budget heavy for model 1. The remaining 3 are mostly mechanical once the pattern is clear.

### M6 — dbt Gold mart (4–7h)

| Subtask | Low | High |
|---|---|---|
| `mart_sales` SQL with joins + FX | 2.5h | 4h |
| Window function for rolling 7d | 1h | 1.5h |
| Tests + verification | 30m | 1.5h |

**Teaching load:** SQL joins (probably new!), window functions (definitely new), jinja in dbt. The single highest-density learning milestone.

### M7 — Streamlit dashboard (3–5h)

| Subtask | Low | High |
|---|---|---|
| Streamlit basics + first chart | 1h | 1.5h |
| Three charts (line, bar, rolling) | 1.5h | 2.5h |
| Polish (titles, formatting) | 30m | 1h |

### M8 — Wire-up + docs + post (4–7h)

| Subtask | Low | High |
|---|---|---|
| `run_pipeline.py` entrypoint | 1h | 1.5h |
| Architecture diagram | 30m | 1h |
| README + screenshots | 1h | 2h |
| Blog post | 2h | 3h |

## Where the estimates are most likely to be wrong

In order of "this is the thing that will eat your time":

1. **The first dbt model.** Universal experience — there's a 2–3 hour stretch where nothing makes sense and then it suddenly does. Not budgetable around; just expect it.
2. **AWS S3 + IAM permissions.** A misconfigured policy that takes 90 minutes to find and 30 seconds to fix.
3. **Joins in `mart_sales`.** If joins are new to you, the FX-conversion join may take longer than estimated. We can decompose it across multiple sessions if it's too much at once.
4. **Python install/environment quirks.** `uv` is great when it works; the 5% of the time it doesn't, it eats an hour.

## Tracking template

Print this or paste it into a Google Sheet. The estimate-vs-actual ratio will be eye-opening.

| Milestone | Subtask | Estimate (h) | Actual (h) | Notes |
|---|---|---|---|---|
| M1 | Repo init | 0.75 | | |
| M1 | Supabase | 0.75 | | |
| M1 | S3 + IAM | 1.5 | | |
| M1 | gitleaks setup | 0.75 | | |
| M1 | Smoke test | 1.75 | | |
| M2 | Seed data | 1.25 | | |
| M2 | Generator | 2.25 | | |
| M2 | Parquet/S3 | 1.25 | | |
| M2 | Verify | 0.75 | | |
| M3 | HTTP client | 0.75 | | |
| M3 | Pydantic | 1.0 | | |
| M3 | Weekend handling | 0.5 | | |
| M3 | S3 write | 0.5 | | |
| M4 | SQLAlchemy | 1.25 | | |
| M4 | Idempotent upsert | 1.5 | | |
| M4 | Verify | 1.25 | | |
| M5 | dbt init | 1.5 | | |
| M5 | First Silver model | 2.5 | | |
| M5 | Remaining Silver | 2.75 | | |
| M5 | Tests | 1.25 | | |
| M6 | mart_sales joins | 3.25 | | |
| M6 | Window functions | 1.25 | | |
| M6 | Tests | 1.0 | | |
| M7 | Streamlit basics | 1.25 | | |
| M7 | Three charts | 2.0 | | |
| M7 | Polish | 0.75 | | |
| M8 | run_pipeline.py | 1.25 | | |
| M8 | Diagram | 0.75 | | |
| M8 | README | 1.5 | | |
| M8 | Blog post | 2.5 | | |

## Final word

If you finish in the low end of these ranges, you likely understood things quickly. If you finish in the high end, you're normal — most people do. If you go significantly over the high end, the answer is almost never "I'm slow" — it's "I've been avoiding a specific milestone." Find the one you've been postponing and do it badly. Done badly is much better than not done.
