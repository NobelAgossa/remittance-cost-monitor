"""BigQuery helpers. Load jobs only: the sandbox forbids DML and streaming inserts."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import date
from pathlib import Path

from google.cloud import bigquery

from ingestion.common.config import Settings


def make_client(settings: Settings) -> bigquery.Client:
    """Create a client using application default credentials and the configured location."""
    return bigquery.Client(project=settings.gcp_project_id, location=settings.bq_location)


def partition_table_id(table_id: str, partition_date: date) -> str:
    """Return the partition decorator form, for example `project.raw.table$20260115`."""
    return f"{table_id}${partition_date:%Y%m%d}"


def load_file_to_partition(
    client: bigquery.Client,
    file_path: Path,
    table_id: str,
    partition_date: date,
    partition_field: str,
    schema: Sequence[bigquery.SchemaField],
) -> int:
    """Replace one day partition of `table_id` with the rows of a local CSV file.

    WRITE_TRUNCATE on the partition decorator replaces that partition only, so running
    the same load twice gives the same result (idempotent). The table is created on the
    first load, partitioned by day on `partition_field`. Every row of the file must have
    `partition_field` equal to `partition_date`, otherwise BigQuery rejects the load.

    Returns the number of rows written by the load job.
    """
    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        schema=list(schema),
        write_disposition=bigquery.WriteDisposition.WRITE_TRUNCATE,
        time_partitioning=bigquery.TimePartitioning(
            type_=bigquery.TimePartitioningType.DAY,
            field=partition_field,
        ),
    )
    destination = partition_table_id(table_id, partition_date)
    with file_path.open("rb") as source_file:
        load_job = client.load_table_from_file(source_file, destination, job_config=job_config)
    load_job.result()
    return load_job.output_rows
