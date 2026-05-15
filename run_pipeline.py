#!/usr/bin/env python3
"""
run_pipeline.py — single entrypoint for dw-mercadolivre.

Runs in sequence:
1. Generate synthetic sales data → S3
2. Fetch Bacen PTAX FX rates → S3
3. Load S3 Parquets → Postgres Bronze
4. Run dbt build (transform + test)
5. Print summary

Usage:
    python run_pipeline.py

This file is a skeleton. It will be completed in Milestone 8
once all ingestion and dbt work is done.
"""

# TODO (Milestone 8): wire up ingestion and dbt calls here
if __name__ == "__main__":
    print("Pipeline entrypoint — not yet implemented. See Milestone 8.")
