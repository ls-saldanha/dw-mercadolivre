# Security Setup

Per ADR-0007. Complete these steps once before starting Milestone 1.

## 1. Create the S3 IAM user

AWS Console → IAM → Users → Create user (no console access, programmatic only).

Add permissions → Create inline policy → JSON tab → paste `iam-policy-s3.json`, replacing `REPLACE-WITH-YOUR-BUCKET-NAME` with your actual bucket name in both Resource lines.

Name the policy `dw-mercadolivre-s3-access`. Generate access keys under Security credentials → Create access key → Application running outside AWS. Save to `.env`.

## 2. Install gitleaks

```bash
# macOS
brew install gitleaks

# verify
gitleaks version
```

## 3. Enable pre-commit hooks

```bash
uv tool install pre-commit
pre-commit install
```

Verify: create a file with a fake key, `git add` it, `git commit` — gitleaks should block it.

## Environment variable names

| Variable | Sensitivity |
|---|---|
| `SUPABASE_URL` | Low |
| `SUPABASE_SERVICE_ROLE_KEY` | Critical — bypasses RLS |
| `AWS_ACCESS_KEY_ID` | Medium |
| `AWS_SECRET_ACCESS_KEY` | Critical |
| `S3_BUCKET` | Low |

## If a secret leaks

1. Rotate immediately at the source (Supabase / AWS).
2. Update `.env`.
3. History scrubbing is cosmetic — rotation is the real fix.
