# Architecture Decision Records

This directory contains ADRs for `dw-mercadolivre`. Each file captures one architectural decision: the context, the decision made, the alternatives considered, and the consequences.

## Index

| ADR | Title | Status |
|---|---|---|
| [0001](0001-use-medallion-architecture.md) | Use Medallion architecture (Bronze/Silver/Gold) | Accepted |
| [0002](0002-meli-as-primary-source.md) | Use Mercado Livre API as primary dynamic source | Superseded by 0009 |
| [0003](0003-synthetic-internal-data.md) | Use synthetic data for internal sales | Accepted |
| [0004](0004-prefect-over-github-actions.md) | Use Prefect Cloud for orchestration | Superseded by 0010 |
| [0005](0005-metabase-over-streamlit.md) | Use Metabase OSS for BI layer | Superseded by 0011 |
| [0006](0006-defer-dbt-ci-to-v2.md) | Defer dbt CI on PRs to v2 | Accepted |
| [0007](0007-security-baseline.md) | Security baseline for v1 | Accepted |
| [0008](0008-claude-md-human-edited-only.md) | CLAUDE.md is human-edited only | Accepted |
| [0009](0009-defer-meli-to-v2.md) | Defer Mercado Livre integration to v2 | Accepted |
| [0010](0010-defer-prefect-to-v2.md) | Defer Prefect orchestration to v2 | Accepted |
| [0011](0011-streamlit-over-metabase-v11.md) | Use Streamlit for v1.1 BI layer | Accepted |

## How to read an ADR

Start with the **Status** line. If it says "Superseded," read the original to understand what we believed at the time, then follow the link to the superseding ADR to see what changed and why.

## How to add a new ADR

Copy `TEMPLATE.md`, increment the number, fill in the sections, and add a row to the index above.
