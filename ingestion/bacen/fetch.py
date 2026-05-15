"""
Bacen PTAX fetcher.

Fetches the USD/BRL exchange rate from the Bacen OLINDA API and writes
it to S3 as Parquet, partitioned by ingestion_date.

Weekend / holiday handling: the API returns an empty list for days with
no rate. We walk back up to LOOKBACK_DAYS to find the most recent
business-day rate.
"""

from datetime import date, timedelta

import httpx
import pandas as pd
from pydantic import BaseModel

from ingestion.common.s3 import write_parquet

BACEN_URL = (
    "https://olinda.bcb.gov.br/olinda/servico/PTAX/versao/v1/odata"
    "/CotacaoDolarDia(dataCotacao='{date}')?$top=1&$format=json"
)
LOOKBACK_DAYS = 7


class _PtaxRate(BaseModel):
    cotacaoCompra: float
    cotacaoVenda: float
    dataHoraCotacao: str


def _fetch_for_date(dt: date) -> _PtaxRate | None:
    """Call the Bacen API for a single date. Returns None if no rate published."""
    url = BACEN_URL.format(date=dt.strftime("%m-%d-%Y"))
    with httpx.Client(timeout=30) as client:
        resp = client.get(url)
        resp.raise_for_status()
    payload = resp.json()
    if not payload["value"]:
        return None
    return _PtaxRate(**payload["value"][0])


def fetch_latest_rate(reference_date: date | None = None) -> tuple[date, _PtaxRate]:
    """Return (effective_date, rate) for the most recent business day.

    Walks back from reference_date (defaults to today) up to LOOKBACK_DAYS.
    Raises ValueError if no rate found within the window.
    """
    if reference_date is None:
        reference_date = date.today()

    for days_back in range(LOOKBACK_DAYS):
        target = reference_date - timedelta(days=days_back)
        rate = _fetch_for_date(target)
        if rate is not None:
            return target, rate

    raise ValueError(
        f"No PTAX rate found within {LOOKBACK_DAYS} days of {reference_date}. "
        "Check if Bacen API is reachable."
    )


def run(reference_date: date | None = None) -> None:
    """Fetch PTAX rate and write to S3. Idempotent — overwrites same-day file."""
    ingest_date = date.today() if reference_date is None else reference_date
    effective_date, rate = fetch_latest_rate(reference_date=ingest_date)

    df = pd.DataFrame(
        [
            {
                "cotacao_date": effective_date.isoformat(),
                "bid_rate": rate.cotacaoCompra,
                "ask_rate": rate.cotacaoVenda,
                "source_timestamp": rate.dataHoraCotacao,
                "_ingested_at": pd.Timestamp.now(tz="UTC"),
            }
        ]
    )

    s3_key = f"bronze/bacen_ptax/ingestion_date={ingest_date.isoformat()}/ptax.parquet"
    write_parquet(df, s3_key)
    print(f"  PTAX effective={effective_date}  bid={rate.cotacaoCompra}  ask={rate.cotacaoVenda}")


if __name__ == "__main__":
    from dotenv import load_dotenv

    load_dotenv()
    run()
