import csv
from datetime import date

from scripts.smoke_test import SCHEMA, run_step, write_smoke_csv


def test_write_smoke_csv_puts_every_row_in_the_partition(tmp_path):
    csv_path = tmp_path / "smoke.csv"

    row_count = write_smoke_csv(csv_path, date(2026, 1, 15))

    with csv_path.open() as csv_file:
        header, *rows = list(csv.reader(csv_file))
    assert header == [field.name for field in SCHEMA]
    assert row_count == len(rows) == 3
    assert {row[0] for row in rows} == {"2026-01-15"}


def test_run_step_reports_pass(capsys):
    assert run_step(1, 4, "works", lambda: None) is True
    assert "PASS  1/4  works" in capsys.readouterr().out


def test_run_step_reports_the_exact_error(capsys):
    def fail() -> None:
        raise ValueError("Access Denied: sandbox limit")

    assert run_step(2, 4, "breaks", fail) is False
    output = capsys.readouterr().out
    assert "FAIL  2/4  breaks" in output
    assert "ValueError: Access Denied: sandbox limit" in output
