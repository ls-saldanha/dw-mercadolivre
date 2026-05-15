> **Note:** This walkthrough was backfilled after the protocol was added to CLAUDE.md. Fields marked `[inferred]` were reconstructed from repo state rather than recorded at the time. Commits and debugging notes referenced inline are real. Future walkthroughs will be written at checkpoint time.

# M1 — Foundation

---

## [2026-05-15] Checkpoint: Repo skeleton

*Commit `279b5e1` — "chore: initialize repo for Milestone 1 foundation"*

**What we built:** Project skeleton — Python environment, all M1 dependencies, security baseline, smoke test draft, and the full docs and ADR tree. Nothing runs yet; this commit is structure only.

**Files touched:**
- `.env.example` — placeholder env vars (no real values)
- `.gitignore` — excludes `.env`, `.venv`, `__pycache__`, etc.
- `.pre-commit-config.yaml` — gitleaks secret scanner + hygiene hooks
- `.python-version` — pins Python 3.13
- `pyproject.toml` — all M1 deps declared (boto3, pydantic, psycopg2-binary, pyarrow, pandas, python-dotenv)
- `CLAUDE.md` — working agreement with Claude Code
- `ingestion/__init__.py`, `ingestion/common/__init__.py` — package structure
- `run_pipeline.py` — stub entrypoint
- `smoke_test.py` — draft smoke test (not yet passing)
- `security/iam-policy-s3.json`, `security/README.md` — S3 least-privilege IAM policy
- `docs/` — PRD, architecture, roadmap, time estimate
- `docs/decisions/` — 11 ADRs (ADR-0001 through ADR-0011)

**New concepts introduced:** [inferred]
- *`uv` package manager* — replacement for pip/poetry; `uv add` adds a dep to pyproject.toml and updates uv.lock
- *`pyproject.toml`* — single config file for project metadata and dependencies; replaces requirements.txt
- *`.gitignore`* — tells git which files to never track (secrets, generated files, virtual envs)
- *`pre-commit` hooks* — shell scripts that run automatically before every `git commit`; if one fails, the commit is blocked
- *gitleaks* — a pre-commit hook that scans for secrets (API keys, passwords) before they reach GitHub
- *Environment variables* — config values injected at runtime via the shell or a `.env` file; never hardcoded in source
- *`.env` file + `python-dotenv`* — `.env` stores local secrets; `load_dotenv()` reads them into `os.environ` at startup
- *IAM policy* — AWS permission document that says exactly what an identity is allowed to do (here: `ListBucket`, `GetObject`, `PutObject` on one bucket only)

**Patterns reused:** None — first milestone.

**What broke and how we fixed it:** No specific breakage documented for this checkpoint (skeleton commit, nothing executed yet).

**Decisions logged:**
- ADR-0001 through ADR-0011 created in `docs/decisions/` — covering architecture choices (medallion, S3, Supabase), deferred scope (MeLi, Prefect, Metabase, dbt CI), and the security baseline.

**Next step:** Wire up real credentials and get the smoke test passing end-to-end.

---

## [2026-05-15] Checkpoint: Smoke test passes — M1 complete

*Commit `5a021f7` — "feat: complete Milestone 1 — foundation smoke test passes"*

**What we built:** Fixed three bugs in `smoke_test.py` (keyword args for psycopg2, `sslmode="require"`, deprecated `utcnow()`), filled the IAM policy with the real bucket name, added `SUPABASE_DB_PASSWORD` to `.env.example`, and documented the debugging session. S3 write/read and Supabase Postgres connect/insert/query all pass green.

**Files touched:**
- `smoke_test.py` — three fixes applied
- `.env.example` — added `SUPABASE_DB_PASSWORD` variable
- `security/iam-policy-s3.json` — filled `<your-bucket-name>` placeholder with real bucket
- `docs/debugging/supabase-connection-errors.md` — real debugging notes added

**New concepts introduced:**
- *psycopg2 keyword args vs URI* — connection strings like `postgresql://postgres:password@host/db` silently misparse passwords containing `@`, `#`, or `%`; keyword args pass the password as a raw string with no parsing
- *`sslmode="require"`* — Supabase enforces SSL on all Postgres connections; without this flag the handshake fails silently on some network configurations
- *`SUPABASE_SERVICE_ROLE_KEY` vs `SUPABASE_DB_PASSWORD`* — the service role key is a JWT for the Supabase HTTP API; it is not the Postgres password. They look similar (both long strings) but are completely different credentials for completely different systems

**Patterns reused:** [inferred] Same `os.getenv()` / `load_dotenv()` pattern used for both S3 and Supabase credentials.

**What broke and how we fixed it** *(from `docs/debugging/supabase-connection-errors.md`)*:

1. **`password authentication failed for user "postgres"`** — `SUPABASE_SERVICE_ROLE_KEY` was used as the Postgres password. That key is a JWT token for the Supabase HTTP API, not the database password. Fix: reset the database password in Supabase dashboard → Settings → Database, store as `SUPABASE_DB_PASSWORD`.

2. **`Connection refused` after repeated failures** — Supabase IP-rate-limits after too many failed auth attempts. The error looks identical to "server is down" but isn't. Fix: wait 5–10 minutes for the block to expire; verify with `nc -zv -w 5 db.<ref>.supabase.co 5432`. Prevention: fix credentials before connecting, not during.

3. **Lesson: errors can change mid-debug** — the error changed from `password authentication failed` → `Connection refused` mid-session. When an error suddenly becomes a *different* error, the problem usually changed too. Re-read what each error actually says rather than assuming it's the same root cause.

**Decisions logged:** ADR-0007 (security baseline — pre-commit gitleaks, explicit credential naming, least-privilege IAM).

**Next step:** Move to M2 — synthetic data generator.

---

## Milestone Complete

M1 closed at commit `5a021f7` on 2026-05-15. Acceptance criterion met: smoke test runs green end-to-end on a clean checkout (S3 write/read + Supabase connect/insert/query).

The real payoff of M1 wasn't the code — it was establishing the security baseline and debugging the Supabase credential confusion early. Both lessons (IAM least-privilege, JWT ≠ DB password) recur constantly in cloud data work.

Next: [m2-synthetic.md](m2-synthetic.md)
