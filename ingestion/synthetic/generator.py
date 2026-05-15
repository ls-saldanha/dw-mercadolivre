"""
generator.py — synthetic sales data generator.

Generates three Parquet files per run (sales, customers, products) and
writes them to S3 under the bronze partition for today's date.

Usage:
    python -m ingestion.synthetic.generator
    python -m ingestion.synthetic.generator --date 2026-05-10
"""

import argparse
import random
from datetime import date, datetime, timezone

import numpy as np
import pandas as pd
from faker import Faker
from dotenv import load_dotenv

from ingestion.common.s3 import write_parquet
from ingestion.synthetic.seed_data import PRODUCTS

load_dotenv()

# Fixed seed in dev so re-running produces the same customer/product catalog.
# Sales get a date-based seed so each day's data is different but still
# reproducible if you need to regenerate a specific date.
CATALOG_SEED = 42
DAILY_SALES_COUNT = 200


def _build_customers(fake: Faker, n: int = 200) -> pd.DataFrame:
    """Generate a fixed catalog of n synthetic customers."""
    random.seed(CATALOG_SEED)
    np.random.seed(CATALOG_SEED)

    rows = []
    for i in range(1, n + 1):
        rows.append(
            {
                "customer_id": f"CUST-{i:04d}",
                "name": fake.name(),
                "email": fake.email(),
                "city": fake.city(),
                "state": fake.state_abbr(),
                "created_at": fake.date_time_between(
                    start_date="-2y", end_date="-30d", tzinfo=timezone.utc
                ),
            }
        )
    return pd.DataFrame(rows)


def _build_products() -> pd.DataFrame:
    """Return the static product catalog from seed_data.py as a DataFrame."""
    return pd.DataFrame(PRODUCTS)


def _build_sales(
    ingestion_date: date,
    customers_df: pd.DataFrame,
    products_df: pd.DataFrame,
    n: int = DAILY_SALES_COUNT,
) -> pd.DataFrame:
    """Generate n sales for a given date, drawing from the customer/product catalogs."""
    # Seed changes per date so each day's orders are different.
    day_seed = int(ingestion_date.strftime("%Y%m%d"))
    random.seed(day_seed)
    np.random.seed(day_seed)

    customer_ids = customers_df["customer_id"].tolist()
    product_ids = products_df["product_id"].tolist()
    prices = dict(zip(products_df["product_id"], products_df["unit_price_brl"]))

    rows = []
    for i in range(1, n + 1):
        pid = random.choice(product_ids)
        qty = random.randint(1, 4)
        rows.append(
            {
                "order_id": f"{ingestion_date.strftime('%Y%m%d')}-{i:05d}",
                "customer_id": random.choice(customer_ids),
                "product_id": pid,
                "quantity": qty,
                "unit_price_brl": prices[pid],
                "total_price_brl": round(prices[pid] * qty, 2),
                "ordered_at": datetime(
                    ingestion_date.year,
                    ingestion_date.month,
                    ingestion_date.day,
                    random.randint(7, 22),
                    random.randint(0, 59),
                    tzinfo=timezone.utc,
                ),
            }
        )
    return pd.DataFrame(rows)


def run(ingestion_date: date | None = None) -> None:
    """Generate and upload all three bronze files for the given date.

    Args:
        ingestion_date: The date partition to generate. Defaults to today.
    """
    if ingestion_date is None:
        ingestion_date = date.today()

    fake = Faker("pt_BR")  # Brazilian locale for realistic names/cities
    date_str = ingestion_date.isoformat()

    print(f"\nGenerating synthetic data for {date_str}...")

    customers_df = _build_customers(fake)
    products_df = _build_products()
    sales_df = _build_sales(ingestion_date, customers_df, products_df)

    write_parquet(customers_df, f"bronze/internal_customers/ingestion_date={date_str}/customers.parquet")
    write_parquet(products_df, f"bronze/internal_products/ingestion_date={date_str}/products.parquet")
    write_parquet(sales_df, f"bronze/internal_sales/ingestion_date={date_str}/sales.parquet")

    print(f"Done. {len(sales_df)} sales, {len(customers_df)} customers, {len(products_df)} products.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", help="YYYY-MM-DD (default: today)", default=None)
    args = parser.parse_args()

    target_date = date.fromisoformat(args.date) if args.date else None
    run(target_date)
