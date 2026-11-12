"""Every DAG file imports without errors. Needs no Airflow database and no network."""

from pathlib import Path

import pytest

DAGS_FOLDER = Path(__file__).resolve().parents[1] / "airflow" / "dags"


@pytest.fixture(scope="module")
def dag_bag(tmp_path_factory):
    with pytest.MonkeyPatch.context() as monkeypatch:
        # Airflow writes its config into AIRFLOW_HOME on import: keep it out of ~/airflow.
        monkeypatch.setenv("AIRFLOW_HOME", str(tmp_path_factory.mktemp("airflow_home")))
        from airflow.dag_processing.dagbag import DagBag

        yield DagBag(dag_folder=DAGS_FOLDER)


def test_dags_have_no_import_errors(dag_bag):
    assert dag_bag.import_errors == {}


def test_hello_dag_is_loaded(dag_bag):
    assert "hello" in dag_bag.dag_ids
