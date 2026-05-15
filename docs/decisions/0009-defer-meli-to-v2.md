# ADR-0009: Defer Mercado Livre integration to v2

**Status:** Accepted
**Date:** 2026-05-14
**Supersedes:** ADR-0002

## Context

ADR-0002 chose Mercado Livre as the primary dynamic data source for v1. That decision assumed the human was fluent in Python and SQL and could absorb OAuth, rate-limit handling, and Pydantic response validation while building. New information: the human is learning Python and SQL alongside this project. Stacking three new concepts (OAuth, retry/backoff, schema validation) on top of an unfamiliar language is a recipe for getting stuck.

## Decision

**Move Mercado Livre integration to v2.** v1.1 uses only the Bacen PTAX API and the synthetic generator. v2 adds MELI as a third source once Python and SQL fundamentals are more comfortable.

## Alternatives considered

- **Keep MELI in v1 with reduced scope** (e.g. anonymous-access only, no OAuth) — Still adds rate-limit and schema-validation concepts. Not enough simplification.
- **Replace MELI with a different API** (e.g. IBGE demographics) — Same problem, different API.
- **Drop external APIs entirely** — Loses the "real data" portfolio story. Bacen is enough to keep that story.

## Consequences

- v1.1 ships faster and with less risk of stalling on auth/network issues
- Portfolio pitch becomes "synthetic sales + real FX rates" instead of "competitive intelligence" — smaller story, still credible
- v2 work is well-scoped: integrate MELI as a known, finished addition rather than building it from scratch while everything else is also new
- The "moved to v2" framing in the README is honest and shows roadmap thinking
