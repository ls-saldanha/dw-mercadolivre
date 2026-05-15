# ADR-0010: Defer Prefect orchestration to v2

**Status:** Accepted
**Date:** 2026-05-14
**Supersedes:** ADR-0004

## Context

ADR-0004 chose Prefect Cloud Hobby tier for orchestration. That choice was sound for a fluent developer but adds a whole new mental model (flows, tasks, deployments, work pools, blocks) on top of Python, SQL, dbt, and S3 — all of which are also new. Five new tools at once is too many.

## Decision

**Move Prefect to v2.** v1.1 uses a single Python entrypoint (`run_pipeline.py`) that orchestrates the steps in order: ingest → load → transform → done. No scheduling, no retries, no Prefect UI. The human runs it manually when they want fresh data.

## Alternatives considered

- **Keep Prefect with minimal scope** (one flow only) — Still requires understanding flows, tasks, deployments. Doesn't materially reduce complexity.
- **GitHub Actions cron instead** — Simpler than Prefect but adds CI concepts and YAML workflow files. Different new tool, still a new tool.
- **No automation at all, just `run_pipeline.py`** — What we chose. Pure Python, nothing new conceptually.

## Consequences

- Pipeline doesn't run on a schedule in v1.1 (manual `python run_pipeline.py` only)
- No screenshot of an orchestration UI for the post — replaced with a screenshot of the dbt lineage graph
- v2 introduction of Prefect is cleaner: the human will have working ingestion and transformation code to wrap in flows, rather than building flows around code they don't fully understand yet
- Honest framing for portfolio: "v1.1 runs on demand; v2 adds Prefect for scheduling and observability"
