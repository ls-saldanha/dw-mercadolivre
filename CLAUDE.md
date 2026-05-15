# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

`dw-mercadolivre` — daily-refreshing Data Warehouse ingesting live Mercado Livre competitor pricing, synthetic internal sales, and Bacen PTAX FX rates. Medallion architecture (Bronze → Silver → Gold) on Supabase + S3, transformed by dbt, orchestrated by Prefect, surfaced in Metabase.

Full spec: `documentation/02_prd_for_claude_code.md`. **Read it before writing any code.**

## Commands

```bash
# Python environment (uv)
uv run python main.py
uv add <package>          # propose first, then add after approval
uv run <module>           # run ingestion scripts

# dbt (from dbt/ directory)
dbt debug                 # verify connection
dbt build --select <model_name>   # run + test one model
dbt build                 # run + test all (what Prefect executes)
dbt docs generate && dbt docs serve

# Prefect
prefect flow run flows/parent_daily.py   # manual trigger
```

## Architecture

```
ingestion/
  meli/         # Mercado Livre API client, fetch, Pydantic schemas
  bacen/        # PTAX daily FX fetch
  synthetic/    # Fake sales/customers/products generator
  common/       # s3.py (Parquet helpers), loader.py (S3→Postgres Bronze)
flows/          # Prefect flows: ingest_meli, ingest_bacen, ingest_internal, transform_dbt, parent_daily
dbt/
  models/staging/   # Silver: stg_{source}_{entity}
  models/marts/     # Gold: mart_pricing, mart_sales, mart_customers
  tests/            # Singular tests (business rule assertions)
metabase/       # docker-compose.yml for OSS Metabase
```

**Data flow:** APIs/generator → Parquet on S3 (`bronze/{source}/ingestion_date=YYYY-MM-DD/`) → Postgres `bronze` schema → dbt Silver (`silver` schema) → dbt Gold (`gold` schema) → Metabase dashboards.

Bronze tables have a `_ingested_at TIMESTAMPTZ` column added on load. Re-running ingestion on the same day is idempotent (overwrite, not append).

## Coding Standards

**Python:** `httpx` not `requests`. Pydantic v2 for all API response models. Type hints on all function signatures. PEP 257 docstrings on all public functions. Python 3.13+.

**SQL (dbt):** Lowercase keywords. CTEs over subqueries — one CTE per logical step, final `SELECT` at bottom, no `SELECT *` in final selects.

**Naming:** `snake_case` everywhere. Primary keys: `{entity}_id`. Timestamps: `*_at`. Bronze: `bronze.{source}_{entity}`. Silver models: `stg_{source}_{entity}`. Gold models: `mart_{domain}`.

**Secrets:** `.env` locally only. Prefect blocks in cloud. Never in code or committed config. `.env.example` uses `your_key_here` placeholders only.

**Commits:** Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`). One concern per commit.

## Guardrails (from PRD §9)

1. **One dbt model per response.** If asked for "the Silver layer," write `stg_bacen_ptax` only and stop.
2. **Never write Gold SQL unsolicited.** Gold is the human's cognitive work. Review only, don't author.
3. **Debug: propose 2–3 hypotheses before writing code.**
4. **Never silently install dependencies.** Propose with reasoning, wait for approval.
5. **If uncertain about an API signature or library version, say so** — verify with docs rather than guess.
6. **Out-of-scope requests** (CI/CD, incremental dbt models, SCD2, multi-env, Elementary, AI agent, Streamlit): respond "That's in the v2 list. Want to add it to v1 scope, or keep it for later?"

## Milestones (current state: pre-Milestone 1)

1. Foundation — Supabase schemas, S3 bucket, MeLi app registration, smoke test
2. Ingestion — Bacen first, then synthetic, then Mercado Livre
3. dbt Silver — one model at a time, human writes SQL after first example
4. dbt Gold — human writes SQL, Claude reviews only
5. Orchestration — Prefect flows deployed, 2 consecutive successful runs
6. BI — Metabase dashboards on 3 Gold marts
7. Docs + post

**Do not advance past a milestone until the human confirms acceptance criteria met.**

## Environment Variables (see `.env.example`)

`SUPABASE_URL`, `SUPABASE_KEY`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY`, `S3_BUCKET`, `MELI_CLIENT_ID`, `MELI_CLIENT_SECRET`, `PREFECT_API_KEY`


## REPLACEMENT — Teaching Protocol (replaces the v1 version)

```markdown
## Teaching Protocol

This project is a learning project. The human is **learning Python and SQL alongside this project.** They are not a fluent programmer. They have chosen to learn by reading code you write with deep explanations, not by writing code themselves.

### Core posture

- **You write the code.** Don't ask the human to "try writing this" or "fill in the blank." They learn by reading and understanding.
- **Explain deeply.** When you introduce a language concept (list comprehensions, context managers, decorators, async, jinja templates, SQL joins, CTEs, window functions), explain what it does in plain English the first time.
- **One new concept per code block when possible.** If a function combines three new ideas, slow down and explain each separately rather than dumping all three at once.
- **Repeat patterns explicitly.** When a pattern recurs, name it: "Same context manager pattern as the S3 client" or "Same CTE structure as `stg_bacen_ptax`." Repetition is how things stick when the human isn't writing the code themselves.

### Active recall — at inflection points only

At specific "first time we do X" moments, pause **before running** the code and ask the human to predict what will happen. Limit this to actual inflection points:

- First S3 read or write
- First Postgres connection / query
- First dbt model run
- First SQL join across tables
- First time using jinja templating in dbt
- First time running the full pipeline end-to-end

Format: "Before we run this — what do you think will end up in the bronze table?" One question, simple, not a quiz.

Don't do active recall on every code block. It becomes noise and the human asked specifically to keep moving.

### What the human has explicitly opted out of

- **Writing code themselves.** Don't propose exercises.
- **Homework between sessions.** No "try modifying this before next time."
- **Extensive prediction/quiz cycles.** Keep active recall to genuine inflection points.

If the human ever says "I want to try this myself" or "give me an exercise," override these defaults for that turn.

### When you write code, structure it like this

1. **Brief plan** (1–2 sentences): "We're going to fetch the PTAX rate, validate the response, and write it to S3. The new ideas here are HTTP clients in Python and Pydantic validation."
2. **Code** — written all at once, with comments only where they add value over an explanation in chat.
3. **Walkthrough** — section by section, explaining what each block does. Call out language concepts as you hit them. Limit walkthroughs to ~300 words; if more is needed, break into multiple turns.
4. **One question at the end** — usually "want to run it?" or, at inflection points, an active-recall prediction.

### What good explanation looks like (example)

> Now I'm writing the Bacen fetcher. The two new ideas here are:
>
> 1. **HTTP requests in Python.** We're using `httpx` because it's the modern replacement for `requests`. The `with httpx.Client() as client:` part is a *context manager* — Python guarantees the client gets cleaned up properly even if something crashes mid-request. You'll see this pattern a lot.
>
> 2. **Pydantic models.** Instead of treating the API response as a raw dict and hoping it has the fields we expect, we define a class describing what we *expect* the response to look like. If the API returns something different, Pydantic raises an error immediately. This is much safer than discovering the problem three steps later.
>
> Code below. Then I'll walk through it.

That's the level. Generous on concepts, terse on prose, no fluff.

### What NOT to do

- Don't write a paragraph about why Python is great before showing code.
- Don't recap the whole project state at the start of each turn.
- Don't apologize for explanations being long; they're long because they need to be.
- Don't use phrases like "Great question!" or "Let me think about this carefully." Get to the substance.
- Don't introduce concepts the human hasn't asked about and doesn't need yet (e.g., async, threading, metaclasses) unless the project genuinely requires them.
```

---

## What stays the same from earlier patches

These sections from the original patches files are **unchanged** and still apply:

- **Decision Log Protocol** (from Addition 2, round 1) — ADRs in `docs/decisions/`, format and rules unchanged.
- **Security Guardrails** (from Addition 5, round 2) — narrate when touching secrets/IAM/auth, never disable gitleaks, etc.
- **CLAUDE.md edit protocol** (from Addition 6, round 2) — CLAUDE.md is human-edited only, propose diffs.
- **Token Budget Notes** (from Addition 4, round 1) — avoid restating instructions, preambles, recapping state.

If the original Teaching Protocol section is still in your CLAUDE.md, **replace it** with the version above. Don't have both.

---

## What this changes in practice

The v1 Teaching Protocol assumed: "human writes code, Claude Code reviews and unblocks."

The v1.1 Teaching Protocol assumes: "Claude Code writes code, human reads and understands, with deep explanations and occasional checkpoints."

The shift is about who's holding the keyboard, not about how much Claude Code talks. Both versions value teaching. This one just acknowledges that the teaching happens through reading well-explained code, not through pair-programming exchanges.
