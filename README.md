# dw-mercadolivre

A daily-refreshing Data Warehouse built on the Medallion architecture, ingesting synthetic e-commerce sales data and live FX rates from Brazil's central bank, transforming through dbt, and surfacing in a Streamlit dashboard.

**Status:** in development — v1.1 scope, building toward v2.

## What this project demonstrates

- Medallion architecture (Bronze → Silver → Gold) on PostgreSQL
- Python-based ingestion with Pydantic validation
- dbt for transformations, testing, and documentation
- AWS S3 as raw data landing zone
- Streamlit for interactive dashboards
- Security baseline: pre-commit secret scanning, least-privilege IAM

## Documentation

| Document | Purpose |
|---|---|
| [docs/PRD.md](docs/PRD.md) | Project specification |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Architectural overview |
| [docs/ROADMAP.md](docs/ROADMAP.md) | v2 and beyond |
| [docs/decisions/](docs/decisions/) | Architecture Decision Records |

## Tech stack

Supabase (PostgreSQL) · AWS S3 · Python 3.13 · dbt-core · Streamlit

## Status

Currently building v1.1. See [docs/ROADMAP.md](docs/ROADMAP.md) for what comes next.

---

*Full README with setup instructions, screenshots, and dashboard link will be published once v1.1 ships.*
