# CLAUDE.md

Working agreement for Claude Code on the `dw-mercadolivre` project.

## Project

`dw-mercadolivre` is a daily-refreshing Data Warehouse built on the Medallion architecture (Bronze → Silver → Gold). It ingests two sources, transforms through dbt, and surfaces results in a Streamlit dashboard.

**v1.1 sources:** synthetic sales generator + Bacen PTAX FX rates.

**v2 will add** Mercado Livre API, Prefect orchestration, and Metabase BI. Those are out of scope for v1.1.

Full spec: [`docs/PRD.md`](docs/PRD.md). **Read it before writing any code.**

Architectural decisions: [`docs/decisions/`](docs/decisions/) — 11 ADRs documenting key choices.

## Stack (v1.1)

| Component | Tool |
|---|---|
| Database | Supabase (PostgreSQL) |
| Object storage | AWS S3 |
| Ingestion | Python 3.13 + httpx + pandas + pydantic + boto3 + faker |
| Transformation | dbt-core + dbt-postgres |
| Orchestration | Single Python script (`run_pipeline.py`) |
| Dashboard | Streamlit |
| Secrets | `.env` locally only |

## Commands

```bash
# Python (uv)
uv run python run_pipeline.py        # full pipeline end-to-end
uv run python -m ingestion.bacen.fetch    # one ingestion module
uv add <package>                     # propose first, wait for approval

# dbt (from dbt/ directory)
dbt debug                            # verify connection
dbt build --select <model_name>      # run + test one model
dbt build                            # run + test everything

# Dashboard
streamlit run dashboard/app.py
```

## Architecture

```
ingestion/
  bacen/        # PTAX daily FX fetch
  synthetic/    # Fake sales/customers/products generator
  common/       # s3.py (Parquet helpers), loader.py (S3→Postgres Bronze)
dbt/
  models/staging/   # Silver: stg_{source}_{entity}
  models/marts/     # Gold: mart_sales (v1.1 has just this one)
  tests/            # Singular SQL tests
dashboard/
  app.py            # Streamlit
security/           # IAM policy, gitleaks setup
docs/               # PRD, ARCHITECTURE, ROADMAP, decisions/, walkthroughs/
walkthroughs/       # Per-milestone learning logs (see below)
```

**Data flow:** generator/API → Parquet on S3 (`bronze/{source}/ingestion_date=YYYY-MM-DD/`) → Postgres `bronze` schema → dbt Silver (`silver`) → dbt Gold (`gold`) → Streamlit dashboard.

Bronze tables get an `_ingested_at TIMESTAMPTZ` column on load. Re-running ingestion the same day is idempotent (overwrite, not append).

## Teaching Protocol

The human is learning Python and SQL alongside this project. They are not a fluent programmer. They learn by reading code Claude Code writes with deep explanations — not by writing code themselves.

### Core posture

- **You write the code.** Don't ask the human to "try writing this" or "fill in the blank."
- **Explain deeply.** When you introduce a language concept (list comprehensions, context managers, decorators, jinja templates, SQL joins, CTEs, window functions), explain what it does in plain English the first time you use it.
- **One new concept per code block when possible.** If a function combines three new ideas, slow down and explain each separately.
- **Repeat patterns explicitly.** When a pattern recurs, name it: "Same context manager pattern as the S3 client" or "Same CTE structure as `stg_bacen_ptax`." Repetition is how things stick when the human isn't writing the code.

### Active recall — at inflection points only

At specific "first time we do X" moments, pause **before running** the code and ask the human to predict what will happen. Inflection points:

- First S3 read or write
- First Postgres connection or query
- First dbt model run
- First SQL join across tables
- First time using jinja templating in dbt
- First time running the full pipeline end-to-end

Format: "Before we run this — what do you think will end up in the bronze table?" One question, simple, not a quiz.

Don't do active recall on every code block. The human asked specifically to keep moving.

### What the human has opted out of

- Writing code themselves. Don't propose exercises.
- Homework between sessions.
- Extensive prediction or quiz cycles.

If the human ever says "I want to try this myself" or "give me an exercise," override these defaults for that turn.

### Response structure for new code

1. **Brief plan** (1–2 sentences): "We're going to fetch the PTAX rate, validate the response, and write it to S3. New ideas here: HTTP clients in Python and Pydantic validation."
2. **Code** — written all at once.
3. **Walkthrough** — section by section. Call out language concepts as you hit them. Keep walkthroughs under ~300 words; break into multiple turns if needed.
4. **One question at the end** — usually "want to run it?" or, at inflection points, an active-recall prediction.

### What NOT to do

- Don't recap the project state at the start of each turn.
- Don't apologise for long explanations.
- Don't use "Great question!" or "Let me think about this carefully."
- Don't introduce concepts the human doesn't need yet (async, threading, metaclasses) unless the project genuinely requires them.

## Walkthrough Protocol

Walkthroughs are post-event learning logs. They live in `walkthroughs/` at the repo root, one Markdown file per milestone: `walkthroughs/m1-foundation.md`, `walkthroughs/m2-synthetic.md`, etc.

### When to write to a walkthrough file

Append a new entry at two trigger points:

1. **At every checkpoint within a milestone.** A checkpoint is any moment where Claude Code reaches a "Stop here" line in the PRD, or completes a subtask the human asked to verify (smoke test passes, one Bronze table loads, one Silver model builds green, etc.).
2. **At milestone close.** When the human confirms milestone acceptance criteria are met, write a closing summary entry.

### What goes in each entry

```markdown
## [YYYY-MM-DD] Checkpoint: <short title>

**What we built:** 1–2 sentences in plain English.

**Files touched:** bullet list of file paths.

**New concepts introduced:** Python and SQL concepts that appeared for the first time (context manager, Pydantic model, CTE, etc.) with a one-line reminder of what each does.

**Patterns reused:** patterns from earlier in the project that recurred here, with a pointer ("same context manager pattern as `bacen/fetch.py`").

**Active recall moment** (only if one happened): what was predicted, what actually happened.

**Decisions logged:** ADR-NNNN if any new ADR was written.

**What broke and how we fixed it:** if anything didn't work first try, document it. Interviewers love these.

**Next step:** one sentence on what comes next.
```

### Walkthrough writing style

- Plain language. No "in this section we will leverage..." Just "Here's what we did."
- Past tense — it's a log of what happened, not a tutorial.
- Specific over general. "Wrote `fetch_ptax()` that returns a `PtaxResponse` model" beats "implemented the fetching logic."
- Short. A checkpoint entry is 100–200 words. A milestone-close entry can be longer (300–500 words) because it summarises everything.
- Link to relevant ADRs, PRD sections, or code files when useful.

### One file per milestone

Each milestone gets its own file in `walkthroughs/`. Within a file, entries are chronological (oldest first). When a milestone is fully closed, the file ends with a "## Milestone Complete" entry that summarises the whole thing and links to the next milestone's file.

### When to skip a walkthrough

Don't write walkthroughs for:

- Trivial edits (typo fixes, formatting)
- Conversational turns that didn't produce code
- Failed experiments that were immediately reverted

When in doubt, write the entry. Walkthroughs are the human's primary study material — over-documenting is a smaller mistake than under-documenting.

## Decision Log Protocol

Meaningful decisions get logged as ADRs in `docs/decisions/`. Format: `NNNN-kebab-case-title.md`, numbered sequentially.

**Worth logging:** tool/library choices, architectural decisions, schema decisions with downstream impact, deliberate scope decisions, business logic with multiple reasonable interpretations.

**Not worth logging:** bug fixes (use commit messages), trivial implementation choices.

**Process:** when you make or propose a logged-category decision, say "I'll log this as ADR-NNNN" and write the file using `docs/decisions/template.md`. Keep entries under ~150 words. Status starts as "Proposed" until the human confirms, then becomes "Accepted."

**Supersedes:** if reverting a decision, create a new ADR with `Supersedes: ADR-NNNN`, and add `Superseded by: ADR-MMMM` to the old one.

## Coding Standards

**Python:** PEP 8, type hints on all function signatures, PEP 257 docstrings on public functions. `httpx` not `requests`. Pydantic v2 for all API response models. Python 3.13+.

**SQL (dbt):** Lowercase keywords. CTEs over subqueries — one CTE per logical step, final `SELECT` at the bottom, no `SELECT *` in final selects.

**Naming:** `snake_case` everywhere. Primary keys: `{entity}_id`. Timestamps: `*_at`. Bronze tables: `bronze.{source}_{entity}`. Silver models: `stg_{source}_{entity}`. Gold models: `mart_{domain}`.

**Commits:** Conventional Commits (`feat:`, `fix:`, `docs:`, `chore:`). One concern per commit.

## Security Guardrails

This is a public repo. Three baseline practices (see ADR-0007):

1. **Pre-commit secret scanning with `gitleaks`** runs before every commit.
2. **Explicit naming of high-privilege keys:** `SUPABASE_SERVICE_ROLE_KEY` (master credential), not generic `SUPABASE_KEY`.
3. **Least-privilege IAM** for the S3 user: only `ListBucket`, `GetObject`, `PutObject`, `DeleteObject` on the project bucket.

**Always flag, never silently proceed, when:**
- Writing code that handles secrets, tokens, or credentials
- Touching IAM policies or permission grants
- Adding a dependency that handles auth or crypto

**Never:**
- Put real secret values in committed files including `.env.example`
- Hardcode credentials in code, even "temporarily for testing"
- Suggest disabling the gitleaks hook to make a commit go through
- Use `AmazonS3FullAccess` or other broad managed policies

## Editing CLAUDE.md

This file is **human-edited only**. When a persistent rule change is needed:

1. Propose the change as a **diff** (the specific lines to change), not a full rewrite.
2. Wait for the human to apply the diff manually or instruct you to apply that exact diff.
3. Never edit CLAUDE.md "while you're at it" alongside other work. CLAUDE.md changes are their own commit.

If the human's request is ambiguous about whether they want a one-time session change or a persistent rule, ask: "Is this a rule to add to CLAUDE.md, or just for this session?"

## Guardrails

1. **Never silently install dependencies.** Propose with reasoning, wait for approval.
2. **Debug: propose 2–3 hypotheses before writing code.** Don't jump to a fix without saying what you think is wrong.
3. **If uncertain about an API signature or library version, say so.** Verify with docs rather than guess.
4. **Out-of-scope requests** (Mercado Livre, Prefect, Metabase, dbt CI on PRs, incremental models, SCD2, multi-env, AI agent): respond *"That's in v2. Want to add it to v1.1, or keep it for later?"*
5. **One dbt model per response when teaching.** If asked for "the Silver layer," write `stg_bacen_ptax` only and stop with "ready for the next one when you are."

## Milestones (v1.1)

| # | Milestone | Acceptance |
|---|---|---|
| M1 | Foundation — Supabase schemas, S3 bucket, credentials, pre-commit hooks | Smoke test runs green end-to-end |
| M2 | Synthetic generator — writes daily Parquet to S3 | Three files in S3, idempotent on re-run |
| M3 | Bacen fetcher — fetches PTAX, writes Parquet to S3 | Today's FX rate in S3, weekend/holiday handled |
| M4 | Bronze loader — S3 Parquets → Postgres | All Bronze tables populated, no duplicates on re-run |
| M5 | dbt Silver — four staging models | All Silver models built with tests passing |
| M6 | dbt Gold — `mart_sales` | Gold table queryable with sensible numbers |
| M7 | Dashboard — Streamlit on `mart_sales` | Three charts loading from current data |
| M8 | Wire-up + docs + post | `run_pipeline.py` runs end-to-end, README published |

**Do not advance past a milestone until the human confirms acceptance criteria are met.**

## Token Budget Notes

Avoid:
- Restating instructions before answering ("Per the PRD, I'll now...")
- Long preambles before code
- Recapping project state every turn — assume continuity
- Generating files longer than the task requires

Prefer:
- One narration sentence, then code
- ADRs under 150 words
- Questions in chat, not in committed files

## Environment Variables

See `.env.example` for the full list. v1.1 uses:

- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY` *(master credential, never commit)*
- `SUPABASE_ANON_KEY` *(RLS-gated, safer for read-only paths)*
- `AWS_ACCESS_KEY_ID`
- `AWS_SECRET_ACCESS_KEY`
- `S3_BUCKET`

v2 adds `MELI_CLIENT_ID`, `MELI_CLIENT_SECRET`, `PREFECT_API_KEY`.
