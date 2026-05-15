# Roadmap: v1.1 → v2

This document is the explicit path from "what we're building now" to "what we originally wanted to build." Each v2 phase is a separately scoped piece of work that can be tackled when you have time and comfort.

The post for v1.1 should mention v2 by name. "I have a roadmap" is a maturity signal in interviews.

---

## v1.1 (current scope)

Built first. See `PRD.md` for the full spec.

What you have when v1.1 is done:
- Daily-refreshable pipeline (run manually)
- 2 data sources (synthetic + Bacen PTAX)
- Bronze → Silver → Gold (1 mart)
- Streamlit dashboard
- dbt docs + ADRs + tests

## v2 — Three independent phases

Each phase is roughly 1–3 weekends of work after v1.1 is shipped. They can be done in any order, but the order below is the one I'd recommend.

### Phase v2a — Add Mercado Livre API

**What it adds:**
- OAuth client credentials flow for MELI
- New ingestion module: `ingestion/meli/`
- Pydantic schemas for MELI responses
- Two new Silver models: `stg_meli_items`, `stg_meli_searches`
- Two new Gold marts: `mart_pricing`, `mart_customers`

**Estimated time:** 15–25 hours

**Why first:** It unlocks the better portfolio story (competitive pricing intelligence), and your Python comfort will be much higher after v1.1 — auth and rate limits will be tractable rather than overwhelming.

**Pre-reqs:** You're comfortable with HTTP, Pydantic, and SQL joins from v1.1.

### Phase v2b — Add Prefect orchestration

**What it adds:**
- Prefect Cloud Hobby tier setup
- Five flows replacing `run_pipeline.py`
- Daily schedule + retries + alerting
- Prefect screenshots for the portfolio post

**Estimated time:** 8–15 hours

**Why second:** Orchestration is most valuable once you have multiple sources running on different cadences. With only Bacen + synthetic from v1.1, the orchestration story is thin. After v2a, you have three sources and a real reason to orchestrate.

**Pre-reqs:** Your ingestion scripts from v1.1 + v2a exist and work end-to-end manually.

### Phase v2c — Swap Streamlit for Metabase

**What it adds:**
- Metabase OSS via Docker Compose
- Read-only Postgres role scoped to Gold schema
- Three Metabase dashboards (one per Gold mart)
- The "self-service BI" portfolio story

**Estimated time:** 5–10 hours

**Why last:** Lowest learning value but highest visible polish. By the time you're here, the rest of the project is solid; this is the showcase layer.

**Pre-reqs:** v2a is done (need the additional Gold marts to make Metabase dashboards interesting).

---

## What v2 does to the portfolio pitch

**v1.1 pitch:** "Daily Data Warehouse with synthetic sales + real FX rates, Medallion architecture, dbt tests, Streamlit dashboard. Roadmap: live competitor pricing, Prefect orchestration, Metabase BI."

**Full v2 pitch:** "Daily-refreshing Data Warehouse ingesting live competitor pricing from Mercado Livre, synthetic transactional data, and central bank FX rates. Medallion architecture, full dbt test coverage, Prefect orchestration with retries and observability, self-service BI through Metabase."

Both are credible. The first is what you ship in 4–8 weeks. The second is what you'll have in 3–6 months if you stay with it.

---

## What NOT to add in v2

These were on the longer wishlist. Push them past v2 or out of scope entirely:

- **dbt CI on PRs** — Add as a smaller change anytime after v2; doesn't need to wait.
- **Incremental materializations + snapshots** — Add when data volume actually demands it. For portfolio scale, full refreshes are fine.
- **Multi-environment (dev/prod)** — Real engineering practice, but adds complexity. Wait until you have a co-worker or contributor who needs it.
- **AI agent layer** — Cool, but its own project. Don't bolt it on; build it separately as v3.
- **CDC from a transactional source** — Out of portfolio scope. Real-world use case but massive overhead.

---

## How to use this roadmap

**While building v1.1:** Don't think about v2. The roadmap exists so you can keep things in scope without losing them.

**When shipping v1.1's post:** Mention v2 by name. "Coming next: Mercado Livre integration, Prefect orchestration, Metabase BI."

**After v1.1 ships:** Take a break of at least a week before starting v2a. You'll come back with fresh eyes and the right level of comfort to learn the new tools without burning out.

**During v2:** Each phase gets its own milestones, ADRs, and acceptance criteria. Don't merge phases — phase v2b should never start until v2a is shipped and stable.
