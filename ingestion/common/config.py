"""Settings loaded from environment variables (documented in `.env.example`)."""

from __future__ import annotations

import os
import re
from collections.abc import Mapping
from dataclasses import dataclass

REQUIRED_VARIABLES = ("GCP_PROJECT_ID", "BQ_LOCATION", "BQ_RAW_DATASET", "ECB_CURRENCIES")
CURRENCY_CODE_PATTERN = re.compile(r"[A-Z]{3}")


class MissingSettingsError(RuntimeError):
    """Raised when required environment variables are missing or empty."""


@dataclass(frozen=True)
class Settings:
    gcp_project_id: str
    bq_location: str
    raw_dataset: str
    ecb_currencies: tuple[str, ...]


def parse_currencies(value: str) -> tuple[str, ...]:
    """Parse a comma-separated list of ISO 4217 codes, for example `"usd, GBP"`."""
    currencies = tuple(code.strip().upper() for code in value.split(",") if code.strip())
    invalid = [code for code in currencies if not CURRENCY_CODE_PATTERN.fullmatch(code)]
    if invalid:
        raise ValueError(f"Invalid currency codes in ECB_CURRENCIES: {', '.join(invalid)}")
    return currencies


def load_settings(environ: Mapping[str, str] = os.environ) -> Settings:
    """Build the settings, failing with every missing variable listed at once."""
    missing = [name for name in REQUIRED_VARIABLES if not environ.get(name, "").strip()]
    if missing:
        raise MissingSettingsError(
            f"Missing environment variables: {', '.join(missing)}. See .env.example."
        )
    return Settings(
        gcp_project_id=environ["GCP_PROJECT_ID"].strip(),
        bq_location=environ["BQ_LOCATION"].strip(),
        raw_dataset=environ["BQ_RAW_DATASET"].strip(),
        ecb_currencies=parse_currencies(environ["ECB_CURRENCIES"]),
    )
