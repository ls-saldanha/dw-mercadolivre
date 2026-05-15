# ADR-0002: Use Mercado Livre API as the primary dynamic source

**Status:** Superseded
**Date:** 2026-05-14
**Superseded by:** ADR-0009

## Context

The project needs at least one real external data source to tell a credible "competitive intelligence" portfolio story. The scope was a Brazilian e-commerce data warehouse, and Mercado Livre is the dominant Brazilian marketplace with a public API.

## Decision

**Use the Mercado Livre API as the primary source of real, dynamic data.** Fetch competitor product listings and prices daily. Use OAuth2 app credentials. Handle rate limits with exponential backoff.

## Alternatives considered

- **Bacen PTAX only (public, no auth)** — simpler, but the portfolio story becomes weaker. No competitive intelligence angle.
- **Web scraping** — no API needed, but fragile and violates ToS.
- **Static CSV seed files** — no real data, weakens the "live pipeline" claim.

## Consequences

- Strong portfolio story: "competitive pricing intelligence from Mercado Livre"
- Requires OAuth2 app registration and token refresh logic
- Rate limit handling needed (Mercado Livre enforces per-minute limits)
- Pydantic schema validation needed for the complex API response structure
- Three new concepts at once for someone learning Python: OAuth, retry/backoff, schema validation

*Note: This decision was superseded when we learned the human is new to Python. See ADR-0009.*
