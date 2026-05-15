# ADR-0011: Use Streamlit for v1.1 BI layer, defer Metabase to v2

**Status:** Accepted
**Date:** 2026-05-14
**Supersedes:** ADR-0005

## Context

ADR-0005 chose Metabase OSS over Streamlit for the BI layer, arguing that Metabase tells the "self-service for non-technical users" story better and is a stronger portfolio signal. That argument is still correct. But Metabase requires Docker, networking between containers and a cloud Postgres, and a read-only role setup — three more new concepts on top of an already-full v1.1.

## Decision

**Use Streamlit for v1.1, defer Metabase to v2.** v1.1's dashboard is a single Python file (`dashboard/app.py`) that connects to the Gold mart and renders three charts. Run locally with `streamlit run dashboard/app.py`.

## Alternatives considered

- **Keep Metabase in v1.1** — Adds Docker, networking, and BI tool concepts. Too much new at once.
- **No dashboard, just dbt docs** — Saves time but the project becomes invisible to non-technical readers of the portfolio post.
- **Hosted Metabase trial** — Saves Docker setup but isn't reproducible for anyone cloning the repo.

## Consequences

- Streamlit is pure Python — the same language the rest of the project uses, so no new mental model
- Dashboard runs locally only for v1.1 (screenshot it for the post)
- The "self-service" portfolio story shifts to v2 — for v1.1 it's "interactive Python dashboard" instead of "BI tool on warehouse"
- Less impressive than Metabase in the post, but actually shippable
- v2 swap to Metabase is a clean addition: the Gold mart already exists, the read-only role is documented, only the BI tool changes
