"""BigQuery sandbox smoke test: proves the design works before any real pipeline is built.

Steps, run against the real sandbox:
  1. load the same CSV twice into one partition with WRITE_TRUNCATE: the rows are replaced,
     not doubled (idempotent load job, no DML);
  2. load the `currency_pegs` dbt seed;
  3. build the `stg_reference__currency_pegs` table model and run its tests;
  4. delete the smoke test table (always runs, even after a failure).

Steps 1 to 3 stop at the first failure and print the exact error.
Run from the repository root:
    uv run --no-sync python -m scripts.smoke_test
"""

from __future__ import annotations

import csv
import sys
import tempfile
from collections.abc import Callable
from datetime import date
from pathlib import Path

from dbt.cli.main import dbtRunner
from dotenv import load_dotenv
from google.cloud import bigquery

from ingestion.common.bigquery import load_file_to_partition, make_client
from ingestion.common.config import load_settings

SMOKE_TABLE = "smoke_test"
PARTITION_FIELD = "event_date"
SCHEMA = (
    bigquery.SchemaField("event_date", "DATE", mode="REQUIRED"),
    bigquery.SchemaField("label", "STRING", mode="REQUIRED"),
)
DBT_DIRECTORIES = ["--project-dir", "dbt", "--profiles-dir", "dbt"]


class SmokeTestError(RuntimeError):
    """Raised when a step runs but does not give the expected result."""


def write_smoke_csv(path: Path, partition_date: date) -> int:
    """Write a small CSV whose rows all belong to `partition_date`; return the row count."""
    rows = [(partition_date.isoformat(), f"row-{number}") for number in range(1, 4)]
    with path.open("w", newline="") as csv_file:
        writer = csv.writer(csv_file)
        writer.writerow([field.name for field in SCHEMA])
        writer.writerows(rows)
    return len(rows)


def check_idempotent_partition_load(
    client: bigquery.Client, table_id: str, location: str, work_dir: Path
) -> None:
    """Load the same file twice into today's partition and check nothing was duplicated."""
    dataset_id = table_id.rsplit(".", 1)[0]
    dataset = bigquery.Dataset(dataset_id)
    dataset.location = location
    client.create_dataset(dataset, exists_ok=True)

    partition_date = date.today()
    csv_path = work_dir / "smoke_test.csv"
    expected_rows = write_smoke_csv(csv_path, partition_date)
    for _ in range(2):
        load_file_to_partition(client, csv_path, table_id, partition_date, PARTITION_FIELD, SCHEMA)

    total_rows = client.get_table(table_id).num_rows

    if total_rows != expected_rows:
        raise SmokeTestError(f"Expected {expected_rows} rows, but found {total_rows}")


def run_dbt(command: list[str]) -> None:
    """Run a dbt command through dbt's Python API; dbt prints its own logs above."""
    result = dbtRunner().invoke([*command, *DBT_DIRECTORIES])
    if not result.success:
        details = result.exception or "see the dbt output above"
        raise SmokeTestError(f"dbt {' '.join(command)} failed: {details}")


def run_step(number: int, total: int, name: str, action: Callable[[], object]) -> bool:
    """Run one step and print PASS, or FAIL with the exact error."""
    try:
        action()
    except Exception as error:  # every failure is reported verbatim, never hidden
        print(f"FAIL  {number}/{total}  {name}\n      {type(error).__name__}: {error}")
        return False
    print(f"PASS  {number}/{total}  {name}")
    return True


def main() -> int:
    load_dotenv()
    settings = load_settings()
    client = make_client(settings)
    table_id = f"{settings.gcp_project_id}.{settings.raw_dataset}.{SMOKE_TABLE}"

    with tempfile.TemporaryDirectory() as work_dir:
        checks: list[tuple[str, Callable[[], object]]] = [
            (
                "load the same partition twice with WRITE_TRUNCATE",
                lambda: check_idempotent_partition_load(
                    client, table_id, settings.bq_location, Path(work_dir)
                ),
            ),
            ("dbt seed currency_pegs", lambda: run_dbt(["seed", "--select", "currency_pegs"])),
            (
                "dbt build stg_reference__currency_pegs (model and tests)",
                lambda: run_dbt(["build", "--select", "stg_reference__currency_pegs"]),
            ),
        ]
        total = len(checks) + 1
        passed = True
        for number, (name, action) in enumerate(checks, start=1):
            if not run_step(number, total, name, action):
                passed = False
                break

    cleaned = run_step(
        total,
        total,
        f"delete {table_id}",
        lambda: client.delete_table(table_id, not_found_ok=True),
    )
    return 0 if passed and cleaned else 1


if __name__ == "__main__":
    sys.exit(main())
