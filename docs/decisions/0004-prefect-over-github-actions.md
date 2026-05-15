# ADR-0004: Use Prefect Cloud for orchestration over GitHub Actions

**Status:** Superseded
**Date:** 2026-05-14
**Superseded by:** ADR-0010

## Context

The pipeline needs to run on a schedule (daily) without manual intervention. Two realistic options for a free, low-ops setup: Prefect Cloud (Hobby tier) and GitHub Actions cron.

## Decision

**Use Prefect Cloud Hobby tier.** Wrap each ingestion step and the dbt build in Prefect tasks and flows. Deploy to Prefect Cloud for scheduling and observability.

## Alternatives considered

- **GitHub Actions cron** — free, no new tool, runs on GitHub's infra. But YAML workflow syntax is unfamiliar and the observability story is weaker (logs only, no flow graph UI).
- **Manual execution only** — simplest possible, but the portfolio doesn't show orchestration skills.
- **Airflow** — industry standard, but heavyweight for a one-person project and complex to self-host for free.

## Consequences

- Prefect Cloud provides a UI showing flow run history, task status, and duration — strong portfolio screenshot
- Prefect flows, tasks, deployments, work pools, and blocks are all new concepts
- Prefect Hobby tier is free but has limits (limited concurrent runs, limited history)
- Adding Prefect while also learning Python, SQL, dbt, and S3 is five new tools at once

*Note: This decision was superseded when we decided to reduce v1 scope. See ADR-0010.*
