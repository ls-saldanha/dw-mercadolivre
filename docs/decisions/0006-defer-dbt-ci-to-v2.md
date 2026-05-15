# ADR-0006: Defer dbt CI on PRs to v2

**Status:** Accepted
**Date:** 2026-05-14

## Context

Running `dbt build` on pull requests (slim CI — only changed models) is a dbt best practice. It catches broken models before they merge. But it requires a GitHub Actions workflow, a CI-specific dbt profile with credentials, and understanding of dbt's `state:modified` selector.

## Decision

**Skip dbt CI on PRs for v1.** All dbt work is done on `main` directly. `dbt build` is run manually (or by `run_pipeline.py`) to validate. Add CI to v2 once dbt concepts are comfortable.

## Alternatives considered

- **Full dbt CI from the start** — best practice, but adds GitHub Actions, secret management in CI, and dbt state concepts. Too much new at once.
- **Lint-only CI (sqlfluff)** — catches style issues but not broken model logic. Marginal value for the added complexity.

## Consequences

- A broken dbt model can merge to `main` undetected until the next pipeline run
- Acceptable risk at v1 scale: one developer, low commit frequency, manual `dbt build` before each push
- v2 CI addition is clean: workflows, profiles, and state concepts can be taught in isolation
