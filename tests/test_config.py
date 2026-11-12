import pytest

from ingestion.common.config import MissingSettingsError, Settings, load_settings, parse_currencies

VALID_ENVIRON = {
    "GCP_PROJECT_ID": "my-project",
    "BQ_LOCATION": "EU",
    "BQ_RAW_DATASET": "raw",
    "ECB_CURRENCIES": "USD,GBP",
}


def test_load_settings_reads_every_variable():
    assert load_settings(VALID_ENVIRON) == Settings(
        gcp_project_id="my-project",
        bq_location="EU",
        raw_dataset="raw",
        ecb_currencies=("USD", "GBP"),
    )


def test_parse_currencies_normalizes_case_and_spaces():
    assert parse_currencies(" usd , GBP,, ") == ("USD", "GBP")


def test_parse_currencies_rejects_invalid_codes():
    with pytest.raises(ValueError, match="EURO"):
        parse_currencies("USD,EURO")


def test_load_settings_lists_every_missing_variable():
    without_currencies = {
        key: value for key, value in VALID_ENVIRON.items() if key != "ECB_CURRENCIES"
    }
    environ = {**without_currencies, "BQ_LOCATION": ""}

    with pytest.raises(MissingSettingsError) as excinfo:
        load_settings(environ)

    message = str(excinfo.value)
    assert "ECB_CURRENCIES" in message
    assert "BQ_LOCATION" in message
