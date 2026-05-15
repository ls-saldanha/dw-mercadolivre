# ADR-0007: Security baseline for v1

**Status:** Accepted
**Date:** 2026-05-14

## Context

The project uses real credentials (Supabase service role key, AWS access keys). A public GitHub repo with accidentally committed secrets causes immediate real-world harm: key rotation, potential AWS bill, possible data breach. A learning project is especially at risk because the human is not yet habituated to credential hygiene.

## Decision

**Enforce a three-layer security baseline:**

1. **`gitleaks` pre-commit hook** — blocks any commit containing a pattern that looks like a secret. Configured in `.pre-commit-config.yaml`.
2. **`detect-private-key` hook** — secondary check from `pre-commit-hooks`.
3. **IAM least-privilege policy** — the S3 IAM user has only `s3:ListBucket`, `s3:GetBucketLocation`, `s3:GetObject`, `s3:PutObject`, `s3:DeleteObject` on the project bucket. No other AWS permissions.

`.env` is always `.gitignore`d. `.env.example` uses `your_key_here` placeholders only.

## Alternatives considered

- **No pre-commit hooks, rely on developer discipline** — not acceptable for a learner. One accidental `git add .env` exposes all credentials.
- **Secrets manager (AWS Secrets Manager, HashiCorp Vault)** — correct for production, overkill and adds cost for a single-developer learning project.
- **GitHub secret scanning only** — catches leaks after push. Pre-commit catches before push. Pre-commit is better.

## Consequences

- Pre-commit hooks must be installed (`pre-commit install`) on every fresh clone — documented in `security/README.md`
- If gitleaks produces a false positive, the human must explicitly allow it (`gitleaks allow` comment) — teaches awareness, not a burden
- Supabase `service_role` key is especially sensitive (bypasses RLS) — flagged in the security README
