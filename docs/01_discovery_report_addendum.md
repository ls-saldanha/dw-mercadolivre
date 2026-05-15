# Discovery Report — Addendum: Scope Right-Sized to v1.1

**Appends to:** `01_discovery_report.md`
**Date:** 2026-05-14

## What changed and why

The original discovery report and v1 PRD assumed the human was a fluent Python and SQL developer learning dbt, S3, Prefect, and Metabase. After more honest calibration, that assumption was wrong: the human is learning Python and SQL alongside this project.

The original scope was buildable for someone fluent. For someone learning the language while learning the tools, it was likely to stall.

**The fix wasn't to cancel the project. It was to right-size it.** v1.1 keeps everything that's pedagogically valuable and ships what's actually achievable. The rest moves to a documented v2 roadmap.

## What stayed

These weren't skill-dependent and stay:
- Medallion architecture (Bronze/Silver/Gold)
- Supabase + S3 + dbt as the core stack
- Real external API (Bacen PTAX)
- Synthetic generator for internal data
- ADRs as the study log
- Security baseline (gitleaks, IAM, env var naming)
- dbt tests as a first-class deliverable

## What moved to v2

- **Mercado Livre API** (ADR-0009): OAuth + rate limits + schema validation = three new tools at once. Will be its own v2 phase once Python comfort is higher.
- **Prefect orchestration** (ADR-0010): A separate mental model on top of an unfamiliar language. v1.1 uses a single Python entrypoint.
- **Metabase BI** (ADR-0011): Docker + networking + BI tool concepts. v1.1 uses Streamlit (just Python).
- **Two of the three Gold marts** (`mart_pricing`, `mart_customers`): The pricing mart needs Mercado Livre; the customer mart needs more SQL fluency. v1.1 ships `mart_sales` only.

## What the portfolio pitch becomes

**Original v1 pitch:** "Daily Data Warehouse ingesting live competitor pricing from Mercado Livre, joining against synthetic internal sales, orchestrated with Prefect, surfaced through Metabase."

**v1.1 pitch:** "Daily-refreshable Data Warehouse using the Medallion architecture, integrating real Brazilian central bank FX rates with synthetic sales data, with full dbt test coverage and an interactive Streamlit dashboard. v2 will add live Mercado Livre competitor pricing, Prefect orchestration, and a Metabase BI layer."

Honest. Smaller. Shippable. The roadmap line at the end is a feature, not a weakness — it shows you can plan beyond what you're holding right now.

## Why this is the right call

A finished smaller project is worth more than an abandoned ambitious one. The metrics that actually matter for a portfolio piece:

1. **Did it ship?** v1.1 will. v1 might not have.
2. **Can the human explain it?** v1.1's narrower scope makes "I can explain every line" achievable. v1 would have had AI-generated code the human didn't fully understand.
3. **Does it tell a coherent story?** Yes. Synthetic sales + real FX rates + warehouse architecture + tests + dashboard is a complete story.
4. **Is the roadmap credible?** Yes. v2 phases are scoped and independent. Anyone reading the README will see a roadmap a real engineer would write.

## What this changed about the timeline

| Metric | v1 estimate | v1.1 estimate |
|---|---|---|
| Total hours | 41–75h | 39–68h |
| Weeks at 2h/day | 4–7 | 4–8 |
| Risk of abandonment | Moderate | Low |
| Risk of finishing but not understanding | High | Low |

Hours are similar — that's because v1.1's smaller scope is offset by a slower per-line pace (learning while building). The change is *what* you spend hours on, not how many.

## The pedagogical pivot

The Teaching Protocol in CLAUDE.md was rewritten for v1.1. Original v1 assumed: "human writes code, Claude reviews." v1.1 assumes: "Claude writes code with deep explanations, human reads and understands, with active-recall checkpoints at inflection points."

Both are valid ways to learn. The new one matches where the human actually is. See `04_claude_md_patches_v11.md` for the protocol text.
