# Discovery Report — Portfolio-Grade Data Warehouse

**Project codename:** `dw-mercadolivre` *(rename as you like)*
**Author:** [Your name]
**Date:** May 2026
**Status:** Discovery complete, ready to build

---

## 1. What we're starting from

The class project builds a Data Warehouse on the **ELT pattern** using the **Medallion architecture**. The stack is Supabase (Postgres), AWS S3 for raw landing, Python for ingestion, and dbt for transformations. Source data is four static files representing an e-commerce business: products, customers, sales, and competitors. Output is a Gold layer organized into Data Marts for Sales, Pricing, and Customer Success.

It's a solid teaching project. It covers the right concepts in the right order: raw landing, typed cleanup, business-ready aggregates. The Medallion split is the industry-standard way to think about layered transformations.

## 2. Why it doesn't work as a portfolio piece (yet)

A hiring manager flipping through GitHub repos in 2026 has seen this exact project shape hundreds of times. The class structure produces a tutorial deliverable, and tutorial deliverables read as "I followed instructions" rather than "I made engineering decisions."

The specific gaps that flag it as tutorial work:

- **The data is static.** A real DW exists because data keeps arriving. A pipeline that processes the same four CSVs forever is closer to a one-time ETL script than a warehouse.
- **No orchestration.** Running `python ingest.py` by hand is not a pipeline. Production data systems run on schedules with retries, observability, and failure handling.
- **No external system integration.** Real DWs aggregate across sources owned by different teams or vendors. A single internal source is the easy case.
- **No quality contract.** The class layers data but doesn't assert what's true about it. dbt's testing capabilities are barely used.
- **No business-facing surface.** The Gold layer is hypothetically ready for BI tools but nothing actually consumes it. The "single version of the truth" promise is unsubstantiated.

None of these are criticisms of the class — a class is the right place to learn the skeleton. They're the gap between "I understand the pattern" and "I can build something that runs."

## 3. The portfolio version: what we're building

**One-line pitch:** A daily-refreshing Data Warehouse that ingests live competitor pricing from the Mercado Livre API, joins it against synthetic internal sales data, enriches with central bank FX rates, and exposes business KPIs through a self-service BI dashboard.

That sentence is the post headline. Everything below is what makes it true.

### Stack

| Layer | Class project | Portfolio version |
|---|---|---|
| Database | Supabase (Postgres) | **Same** — proven, free tier, S3-compatible storage |
| Data lake | S3 (Parquet) | **Same** |
| Ingestion | Python + Boto3/Pandas | **Same**, but hitting live APIs instead of reading static files |
| Transformation | dbt | **Same**, plus dbt tests as a first-class deliverable |
| Orchestration | None (manual runs) | **Prefect Cloud Hobby tier** — scheduled flows, retries, observability |
| BI / consumption | None | **Metabase OSS** self-hosted, connected to the Gold layer |

### Data sources

| Source | Type | Auth | Refresh | Why |
|---|---|---|---|---|
| **Mercado Livre API** | Public REST API | OAuth (registered app) | Daily | Real, dynamic, competitively relevant data. "I integrated with an OAuth API" is a stronger story than "I read a CSV." |
| **Bacen PTAX** | Public REST API | None | Daily | USD/BRL FX rate enrichment. One-line addition, big payoff: Gold layer can report revenue in both currencies, which is how Brazilian e-commerce actually thinks about pricing. |
| **Synthetic sales generator** | Python script | N/A | Daily, incremental | "Internal" data representing our company's sales, customers, products. Keeps the story coherent without needing a real e-commerce backend. Demonstrates incremental loading. |

### Architecture (layer by layer)

**Bronze.** Raw landing zone in S3, partitioned by source and ingestion date. Files are Parquet for compression and column-pruning benefits. Schemas mirror the source APIs exactly — no transformations, no opinions. This is the "what arrived" layer. If anything downstream is wrong, we can rebuild from Bronze without re-hitting the APIs.

**Silver.** Typed, cleaned, conformed. Each Bronze table gets a corresponding Silver model that fixes types, standardizes naming (snake_case, UTC timestamps), handles nulls and duplicates, and applies business-light classifications (e.g., price-tier buckets). Surrogate keys are added here. This is the "what we trust" layer.

**Gold.** Business-facing marts. Three of them, each tied to a stakeholder question:

- `mart_pricing` — Are our prices competitive? Joins our products to Mercado Livre listings of similar products, calculates a competitive-index metric per SKU per day, with FX-adjusted USD equivalents.
- `mart_sales` — What's our revenue trend? Daily/weekly/monthly aggregates with year-over-year comparisons, by category and customer segment.
- `mart_customers` — Who are our best customers and who are we losing? RFM-style segmentation, churn indicators, lifetime value cohorts.

These three marts are what Metabase reads. They're also the layer an AI agent (Claude, Gemini, etc.) would query for natural-language business questions, which is a story to tell in the post even if you don't build the agent itself in v1.

### Orchestration

Prefect Cloud Hobby tier. One flow per source (Mercado Livre, Bacen, synthetic generator), one flow to run `dbt build`, and a parent flow that orchestrates them in order on a daily schedule. Retries on API failures, alerting on test failures, and a UI you can screenshot for the post.

### Quality

dbt tests are not optional. Every Silver model has at minimum a `not_null` test on its primary key and a `unique` test on its natural key. Foreign-key relationships are asserted with `relationships` tests. Custom singular tests catch business logic violations (e.g., "no order has zero items"). The test suite runs as part of `dbt build` on every pipeline run; failures stop the pipeline and notify Prefect.

### BI surface

Metabase OSS in Docker, connected to Supabase with a read-only role scoped to the Gold schema. Three saved dashboards corresponding to the three marts. The dashboards are not the engineering work — they're the proof the engineering work matters.

## 4. What we're deliberately not building in v1

Naming this list is part of the discipline. Scope discipline is a portfolio signal in itself.

- **dbt CI on pull requests.** Will add in v2. v1 runs tests on every pipeline run, which is enough.
- **Incremental dbt models.** v1 rebuilds Silver/Gold on every run. Fine at this data volume. v2 introduces `incremental` materializations and `dbt snapshots` for SCD2 tracking of competitor prices.
- **CDC from a transactional source.** Out of scope. Synthetic generator is sufficient.
- **AI agent on top of Gold.** Mention in the post as "next step," don't build.
- **Multi-environment (dev/prod) separation.** v2 work. v1 has one environment.
- **Cost monitoring, data observability tooling (Monte Carlo / Elementary).** v2.

## 5. The portfolio story this lets you tell

In your post and your interviews, you can claim — and back up with code — the following:

1. You designed an ELT pipeline integrating multiple external APIs with different auth models.
2. You implemented the Medallion architecture with clear separation of concerns between raw, conformed, and business layers.
3. You orchestrated the pipeline with a production-grade workflow tool, including scheduling, retries, and observability.
4. You wrote a data quality test suite that runs on every refresh and blocks downstream consumption on failure.
5. You exposed the warehouse through a self-service BI tool, demonstrating the architectural payoff.
6. You documented data lineage automatically using dbt's `docs generate`.

That's six concrete, verifiable claims. Most tutorial-grade portfolios have one or two.

## 6. Risks and open questions (honest list)

- **Mercado Livre API auth.** The public docs are inconsistent about whether `/sites/{site}/search` requires OAuth or works anonymously. Plan: register an app upfront (10 minutes, free). If anonymous works for our endpoints, we use it; OAuth is the documented fallback.
- **Metabase + Supabase wiring.** Should work over standard Postgres connection, but verify during Milestone 5. Documented fallback: Streamlit on Streamlit Cloud.
- **API rate limits.** Mercado Livre rate-limits anonymous access more aggressively than authenticated. Plan: cache responses, fetch a small product catalog (maybe 50–100 SKUs in 2–3 categories), don't try to scrape the whole site.
- **Prefect free tier limits.** 5 deployed workflows, 500 serverless minutes/month. Sufficient for v1; consolidate flows if we get close.

## 7. Timeline (working days, not hours)

Assuming ~2 hours of focused work per day. Adjust to your actual availability.

- **Day 1–2.** Local setup. Supabase project, S3 bucket, Mercado Livre app registration, Prefect Cloud account, dbt project skeleton. Verify all credentials work end-to-end with a smoke test.
- **Day 3–4.** Ingestion. Synthetic generator + Mercado Livre fetcher + Bacen fetcher. Land Parquet to S3 Bronze. Load Bronze tables into Supabase.
- **Day 5–6.** Silver and Gold dbt models. Write tests as you go, not after.
- **Day 7.** Prefect flows and scheduling.
- **Day 8.** Metabase setup and dashboards.
- **Day 9.** Documentation, README, screenshots, dbt docs published.
- **Day 10.** Write the post.

If you slip, slip the dashboard before slipping the tests. Tests are the credibility; dashboard is the screenshot.

---

## Appendix A — The story for your post

A draft outline you can fill in once it's built:

- The problem (why DWs exist, why "spreadsheet hell" is real)
- The architecture (a diagram of the three layers + sources + consumers)
- The interesting engineering decisions (why Prefect over Airflow, why Metabase over a custom dashboard, why we kept synthetic data alongside real)
- One thing that broke and how you fixed it (interviewers love this — keep a notes file as you build)
- What you'd do differently next time (the v2 list above)
- Links: repo, dbt docs site, screenshots of the Prefect UI and Metabase dashboards

Don't write the post until the project runs end-to-end at least three times in a row without manual intervention. A post about a fragile project is worse than no post.
