"""ECB euro foreign exchange reference rates (implemented in week 3).

Source: ECB Data Portal, SDMX REST API, no API key. Series key `D.{CURRENCIES}.EUR.SP00.A`
with `format=csvdata`. Values are units of the foreign currency per 1 EUR, published on
working days only.
"""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date

ECB_API_BASE_URL = "https://data-api.ecb.europa.eu/service/data/EXR/"


def fetch_fx_rates(start: date, end: date, currencies: Sequence[str]) -> None:
    """Fetch, validate and load ECB reference rates for a date range.

    Calls the ECB API for `currencies` between `start` and `end`, parses the CSV
    response and validates it (currency codes, positive numeric values, unique date and
    currency). Writes a local file, then loads it into the matching date partitions of
    `raw.ecb_fx_rates` with WRITE_TRUNCATE. Retries with backoff on network errors.
    A day without publication (weekend or holiday) is not an error.
    """
    raise NotImplementedError("ECB ingestion is implemented in week 3 (see docs/PLAN.md).")
