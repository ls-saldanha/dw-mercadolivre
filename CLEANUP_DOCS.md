Docs Cleanup — Run This Once
Instructions for Claude Code: Execute every task in order. Do not skip any step. When done, verify the final structure matches the tree in Task 11, then delete this file.
Run all file operations from the repo root.

Task 8 — Fix internal cross-references
Several documents reference others by old filenames. Search for and update these references:
Old reference
New reference
02_prd_v11.md
PRD.md
02_prd_for_claude_code.md
PRD.md (in historical context only) or delete the reference
03_time_estimate_v11.md
time-estimate.md
03_time_estimate.md
time-estimate.md
06_roadmap_v1_to_v2.md
ROADMAP.md
01_discovery_report.md
ARCHITECTURE.md
01_discovery_report_addendum.md
ARCHITECTURE.md (the addendum is now a section inside it)
01.5_discovery_report_addendum.md
ARCHITECTURE.md
dw_mercadolivre_spec_v11.md
PRD.md
dw_jornada_pro_*.md
check context: usually PRD.md or delete
00_repo_architecture.md
delete reference, or replace with docs/README.md
TEMPLATE.md (in ADR contexts)
template.md
Files to grep through:
	•	All .md files in docs/
	•	All .md files in docs/decisions/
	•	CLAUDE.md at repo root
	•	README.md at repo root (if it exists yet)
For each match, update the link or reference to the new filename. If a reference is in a historical-context section explaining what something used to be called, you may leave it but flag it for review.
After this task, run grep -r "02_prd_v11\|03_time_estimate_v11\|06_roadmap_v1_to_v2\|01_discovery_report\|dw_mercadolivre_spec_v11\|00_repo_architecture" docs/ CLAUDE.md README.md 2>/dev/null and confirm zero matches (other than in the historical sections you flagged).


Task 10.5 — Write a minimum-viable root README.md
Check whether README.md at the repo root is empty or near-empty (fewer than ~10 lines of substantive content).
If yes, create a placeholder README. This is not the final README — it will be expanded after Milestone 8 with screenshots, the published dashboard URL, and the final pitch. For now, the placeholder prevents the repo from looking abandoned to anyone who lands on it.
File: README.md at repo root.
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
If README.md already has substantive content (more than ~10 lines, real prose), do not overwrite. Show the human what's there and ask before changing.

After completing all tasks, print the contents of docs/ (recursive) using ls -la docs/ docs/decisions/ or find docs -type f. The result should match this exactly:
docs/
├── README.md
├── PRD.md
├── ARCHITECTURE.md
├── ROADMAP.md
├── time-estimate.md
└── decisions/
    ├── README.md
    ├── template.md
    ├── 0001-use-medallion-architecture.md
    ├── 0002-meli-as-primary-source.md
    ├── 0003-synthetic-internal-data.md
    ├── 0004-prefect-over-github-actions.md
    ├── 0005-metabase-over-streamlit.md
    ├── 0006-defer-dbt-ci-to-v2.md
    ├── 0007-security-baseline.md
    ├── 0008-claude-md-human-edited-only.md
    ├── 0009-defer-meli-to-v2.md
    ├── 0010-defer-prefect-to-v2.md
    └── 0011-streamlit-over-metabase-v11.md
If the actual structure does not match (extra files, missing files, wrong names), list the discrepancies and stop. Do not delete this file until everything is correct.
Note: 0011-streamlit-over-metabase-v11.md retains the -v11 in its filename because that's part of the original ADR slug, not a version suffix on the filename. Leave it as-is.

Task 12 — Stage and commit
After verification passes, stage all changes and commit with this message:
docs: reorganize to professional naming conventions

- Rename PRD spec, ARCHITECTURE, ROADMAP to canonical uppercase
- Merge discovery report + addendum into ARCHITECTURE.md
- Drop numbered prefixes (01_, 02_, etc.) from filenames
- Drop _v11 version suffixes (git tracks versions)
- Rename ADR template to lowercase per MADR convention
- Add docs/README.md as table of contents
- Add placeholder root README.md
- Delete superseded v1 files and redundant 00_repo_architecture.md
Do not push. The human will review the commit first.

Task 13 — Delete this file
After Task 12 completes successfully, delete this file (CLEANUP_DOCS.md or whatever filename it was saved as).
Then respond with:
"Docs cleanup complete. Tree matches the spec. Ready for review before push."
