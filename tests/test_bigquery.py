from datetime import date
from unittest.mock import create_autospec, patch

from google.cloud import bigquery

from ingestion.common.bigquery import load_file_to_partition, make_client, partition_table_id
from ingestion.common.config import Settings

TABLE_ID = "my-project.raw.events"
SCHEMA = [
    bigquery.SchemaField("event_date", "DATE"),
    bigquery.SchemaField("value", "INT64"),
]


def test_partition_table_id_appends_the_date_decorator():
    assert partition_table_id(TABLE_ID, date(2026, 1, 15)) == "my-project.raw.events$20260115"


def test_load_file_to_partition_truncates_only_the_target_partition(tmp_path):
    csv_file = tmp_path / "events.csv"
    csv_file.write_text("event_date,value\n2026-01-15,1\n2026-01-15,2\n")
    client = create_autospec(bigquery.Client, instance=True)
    client.load_table_from_file.return_value.output_rows = 2

    rows = load_file_to_partition(
        client, csv_file, TABLE_ID, date(2026, 1, 15), "event_date", SCHEMA
    )

    assert rows == 2
    _, destination = client.load_table_from_file.call_args.args
    job_config = client.load_table_from_file.call_args.kwargs["job_config"]
    assert destination == "my-project.raw.events$20260115"
    assert job_config.write_disposition == bigquery.WriteDisposition.WRITE_TRUNCATE
    assert job_config.source_format == bigquery.SourceFormat.CSV
    assert job_config.skip_leading_rows == 1
    assert job_config.time_partitioning.field == "event_date"
    assert job_config.time_partitioning.type_ == bigquery.TimePartitioningType.DAY
    client.load_table_from_file.return_value.result.assert_called_once()


def test_make_client_uses_configured_project_and_location():
    settings = Settings("my-project", "EU", "raw", ("USD",))
    with patch("ingestion.common.bigquery.bigquery.Client") as client_class:
        make_client(settings)
    client_class.assert_called_once_with(project="my-project", location="EU")
