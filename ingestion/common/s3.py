"""
s3.py — thin wrapper around boto3 for writing/reading Parquet on S3.

All ingestion modules (bacen, synthetic) call write_parquet() instead of
touching boto3 directly. One place to change if we swap storage backends.
"""

import io
import os
import boto3
import pandas as pd


def _client() -> boto3.client:
    """Create an S3 client from environment variables."""
    return boto3.client(
        "s3",
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
        region_name=os.environ["AWS_DEFAULT_REGION"],
    )


def write_parquet(df: pd.DataFrame, s3_key: str) -> None:
    """Write a DataFrame to S3 as a Parquet file.

    Args:
        df: The DataFrame to write.
        s3_key: Path inside the bucket, e.g. ``bronze/bacen_ptax/ingestion_date=2026-05-15/ptax.parquet``.
    """
    bucket = os.environ["S3_BUCKET"]
    buf = io.BytesIO()
    df.to_parquet(buf, index=False)
    buf.seek(0)
    _client().put_object(Bucket=bucket, Key=s3_key, Body=buf.getvalue())
    print(f"  wrote s3://{bucket}/{s3_key} ({len(df)} rows)")


def read_parquet(s3_key: str) -> pd.DataFrame:
    """Read a Parquet file from S3 into a DataFrame.

    Args:
        s3_key: Path inside the bucket.
    """
    bucket = os.environ["S3_BUCKET"]
    obj = _client().get_object(Bucket=bucket, Key=s3_key)
    return pd.read_parquet(io.BytesIO(obj["Body"].read()))
