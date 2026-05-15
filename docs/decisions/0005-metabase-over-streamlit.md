# ADR-0005: Use Metabase OSS for the BI layer over Streamlit

**Status:** Superseded
**Date:** 2026-05-14
**Superseded by:** ADR-0011

## Context

The project needs a BI layer to surface the Gold mart. The target audience for the portfolio is non-technical readers who want to see a real dashboard, plus technical readers who want to see modern stack choices.

## Decision

**Use Metabase OSS.** Run via Docker Compose, connect to Supabase Postgres with a read-only role. Metabase tells the "self-service BI for non-technical users" story that Streamlit cannot.

## Alternatives considered

- **Streamlit** — pure Python, no Docker, lower setup cost. But it's a developer tool, not a BI tool — it doesn't tell the same "non-technical user" story.
- **Grafana** — good for time-series, but the SQL-heavy dashboard model fits better in Metabase.
- **Redash** — similar to Metabase but less polished UI and smaller community.

## Consequences

- Metabase dashboard is a stronger portfolio signal than a Streamlit app for a DW project
- Requires Docker, Docker Compose, a read-only Postgres role, and networking between containers and cloud Postgres
- Three more new concepts on top of an already-full v1
- Metabase config is not code — it's clicks in a UI, which is harder to version and reproduce

*Note: This decision was superseded when we decided to reduce v1 scope. See ADR-0011.*
