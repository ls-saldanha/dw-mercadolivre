"""
smoke_test.py — Milestone 1 acceptance check.

Verifies all infrastructure is reachable:
  1. Reads credentials from .env
  2. Writes a 1-row Parquet to S3, reads it back
  3. Connects to Supabase Postgres, inserts a row to bronze.smoke_test, queries it
"""

import os
import io
import time
import pandas as pd
import boto3
import psycopg2
from dotenv import load_dotenv

load_dotenv()


def check_env() -> None:
    required = [
        "SUPABASE_URL",
        "SUPABASE_SERVICE_ROLE_KEY",
        "SUPABASE_DB_PASSWORD",
        "AWS_ACCESS_KEY_ID",
        "AWS_SECRET_ACCESS_KEY",
        "AWS_DEFAULT_REGION",
        "S3_BUCKET",
    ]
    missing = [k for k in required if not os.getenv(k)]
    if missing:
        raise EnvironmentError(f"Missing env vars: {missing}")
    print("✓ All env vars present")


def test_s3() -> None:
    s3 = boto3.client(
        "s3",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        region_name=os.getenv("AWS_DEFAULT_REGION"),
    )
    bucket = os.getenv("S3_BUCKET")
    key = "smoke_test/smoke.parquet"

    df = pd.DataFrame([{"id": 1, "message": "smoke_ok", "ts": pd.Timestamp.now("UTC")}])

    buf = io.BytesIO()
    df.to_parquet(buf, index=False)
    buf.seek(0)
    s3.put_object(Bucket=bucket, Key=key, Body=buf.getvalue())
    print(f"✓ S3 write: s3://{bucket}/{key}")

    obj = s3.get_object(Bucket=bucket, Key=key)
    result = pd.read_parquet(io.BytesIO(obj["Body"].read()))
    assert result["message"].iloc[0] == "smoke_ok"
    print(f"✓ S3 read: {len(result)} row(s) returned")


def _supabase_conn_params() -> dict:
    # SUPABASE_URL looks like: https://<project-ref>.supabase.co
    # Postgres host is: db.<project-ref>.supabase.co
    # Password is the DB password from Supabase Settings → Database (NOT the service role key)
    url = os.getenv("SUPABASE_URL", "")
    project_ref = url.replace("https://", "").replace(".supabase.co", "")
    return {
        "host": f"db.{project_ref}.supabase.co",
        "port": 5432,
        "dbname": "postgres",
        "user": "postgres",
        "password": os.getenv("SUPABASE_DB_PASSWORD", ""),
        "sslmode": "require",
        "connect_timeout": 10,
    }


def test_postgres() -> None:
    conn = psycopg2.connect(**_supabase_conn_params())
    cur = conn.cursor()

    cur.execute("""
        create table if not exists bronze.smoke_test (
            id serial primary key,
            message text not null,
            _ingested_at timestamptz default now()
        )
    """)
    conn.commit()

    cur.execute("insert into bronze.smoke_test (message) values (%s)", ("smoke_ok",))
    conn.commit()
    print("✓ Postgres write: inserted row into bronze.smoke_test")

    cur.execute("select count(*) from bronze.smoke_test")
    count = cur.fetchone()[0]
    print(f"✓ Postgres read: {count} row(s) in bronze.smoke_test")

    cur.close()
    conn.close()


if __name__ == "__main__":
    start = time.time()
    print("\n── Smoke Test ──────────────────────")
    check_env()
    test_s3()
    test_postgres()
    elapsed = time.time() - start
    print(f"── All checks passed in {elapsed:.1f}s ──\n")
