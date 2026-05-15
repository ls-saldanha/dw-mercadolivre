# Debugging: Supabase Postgres Connection Errors

Documented from Milestone 1 setup. Real errors encountered, real fixes.

---

## Error 1: `password authentication failed for user "postgres"`

**What it means:** TCP connection reached the server, but the password was wrong.

**Why it happened here:** `SUPABASE_SERVICE_ROLE_KEY` was used as the Postgres password. That key is a JWT token for the Supabase HTTP API — it is not the database password. These are two completely different credentials.

| Credential | What it is | Used for |
|---|---|---|
| `SUPABASE_SERVICE_ROLE_KEY` | JWT token | Supabase REST API / Auth API |
| `SUPABASE_DB_PASSWORD` | Postgres password | Direct psycopg2 / SQLAlchemy connections |

**Fix:** Supabase dashboard → Settings → Database → "Database password" → reset and copy. Store as `SUPABASE_DB_PASSWORD` in `.env`.

---

## Error 2: `Connection refused` after repeated failed attempts

**What it means:** The TCP connection didn't even reach Postgres — the server's firewall rejected it.

**Why it happened here:** Supabase has IP-level rate limiting. After too many failed authentication attempts in a short window, it temporarily blocks the offending IP at the network level. The error looks identical to "server is down" but the cause is different.

**How to distinguish "server down" from "IP banned":**
- If you got `password authentication failed` first, then `Connection refused` — you're probably banned.
- If you only ever get `Connection refused` — check if the project is paused (free tier pauses after ~1 week of inactivity).

**Fix:**
1. Supabase dashboard → scroll down in the project overview — there may be a ban/alert notice to dismiss.
2. Wait 5–10 minutes for the temporary block to expire.
3. Verify with `nc -zv -w 5 db.<project-ref>.supabase.co 5432` — if it returns "Connection refused", ban is still active. If it returns "succeeded", you're clear.

**Prevention:** Don't run a connection script in a tight loop while troubleshooting credentials. Fix the credentials first, then connect once.

---

## Lesson: Error messages can change mid-debug

During this session the error changed from:
1. `password authentication failed` → wrong credential type
2. `Connection refused` → IP ban from repeated failures

When an error suddenly becomes a *different* error, the problem usually changed — don't assume the second error is the same root cause. Re-read what each error actually says.

---

## Reference: Supabase connection params for psycopg2

```python
# Use keyword arguments, not a connection string URI.
# Special characters in passwords break URI parsing.
conn = psycopg2.connect(
    host=f"db.{project_ref}.supabase.co",
    port=5432,
    dbname="postgres",
    user="postgres",
    password=os.getenv("SUPABASE_DB_PASSWORD"),
    sslmode="require",
    connect_timeout=10,
)
```

Why `sslmode="require"`: Supabase enforces SSL on all connections. Without it, the handshake may fail silently on some network configurations.

Why keyword args over URI: If your password contains `@`, `#`, `%`, or other special characters, a URI like `postgresql://postgres:p@ss#word@host/db` will be parsed incorrectly — the `@` in the password looks like the host separator. Keyword args pass the password as a raw string with no parsing.
