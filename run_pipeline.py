#!/usr/bin/env python3
"""
run_pipeline.py — single entrypoint for dw-mercadolivre.

Runs the full pipeline in order:
  1. Generate synthetic sales data → S3
  2. Fetch Bacen PTAX FX rate → S3
  3. Load S3 Parquets → Postgres Bronze
  4. dbt build (Silver + Gold transforms + all tests)

Usage:
    uv run python run_pipeline.py
    uv run python run_pipeline.py --date 2026-05-10
"""

import argparse
import subprocess
import sys
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

from ingestion.bacen.fetch import run as run_bacen
from ingestion.common.loader import run as run_loader
from ingestion.synthetic.generator import run as run_synthetic


def run_dbt() -> None:
    """Run dbt build using the same venv as the current Python process."""
    dbt = Path(sys.executable).parent / "dbt"
    subprocess.run(
        [str(dbt), "build", "--profiles-dir", "dbt", "--project-dir", "dbt"],
        check=True,
    )


def main(pipeline_date: date | None = None) -> None:
    today = pipeline_date or date.today()
    print(f"\n=== dw-mercadolivre pipeline — {today} ===")

    print("\n[1/4] Synthetic data → S3")
    run_synthetic(today)

    print("\n[2/4] Bacen PTAX → S3")
    run_bacen(today)

    print("\n[3/4] S3 Parquets → Postgres Bronze")
    run_loader(today)

    print("\n[4/4] dbt build (Silver + Gold + tests)")
    run_dbt()

    print("\n=== Pipeline complete ===\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", help="YYYY-MM-DD (default: today)", default=None)
    args = parser.parse_args()

    target_date = date.fromisoformat(args.date) if args.date else None
    main(target_date)
