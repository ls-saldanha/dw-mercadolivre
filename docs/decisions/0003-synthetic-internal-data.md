# ADR-0003: Use synthetic data for internal sales, customers, and products

**Status:** Accepted
**Date:** 2026-05-14

## Context

The project needs an internal sales dataset to join against external pricing data. No real sales database exists (this is a learning project, not a production system). The data needs to be realistic enough to make the Gold mart and dashboard meaningful.

## Decision

**Generate synthetic internal data using Python (`Faker` + `numpy.random`).** Three entities per day: sales, customers, products. Fixed seed in dev mode for reproducibility. ~200 sales/day, ~50 SKUs, ~200 customers. Written as Parquet to S3 Bronze, then loaded to Postgres.

## Alternatives considered

- **Public dataset (e.g., Brazilian IBGE, Kaggle)** — no control over schema, may not fit the project's model. Harder to make idempotent daily writes.
- **Static CSV loaded once** — no "daily ingestion" pattern. Pipeline looks less like a real pipeline.
- **Real sales data from a client** — not available, not appropriate for a public portfolio project.

## Consequences

- Full control over schema — can add columns, change types, add edge cases at will
- Data is always available, no API keys or rate limits
- Portfolio disclaimer needed: "internal data is synthetic" (honest and standard in portfolio projects)
- Faker teaches a useful Python library; numpy.random teaches reproducibility via seeds
- Incremental daily files demonstrate partitioned ingestion pattern
