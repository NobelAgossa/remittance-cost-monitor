"""The Airflow image runs the same versions as the local environment (pyproject.toml)."""

import re
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def read_dockerfile() -> str:
    return (ROOT / "airflow" / "Dockerfile").read_text()


def read_pyproject() -> dict:
    return tomllib.loads((ROOT / "pyproject.toml").read_text())


def pyproject_pins() -> dict[str, str]:
    pyproject = read_pyproject()
    requirements = list(pyproject["project"]["dependencies"])
    for group in pyproject["dependency-groups"].values():
        requirements.extend(group)
    return dict(requirement.split("==") for requirement in requirements)


def test_base_image_matches_airflow_and_python_pins():
    match = re.search(r"^FROM apache/airflow:(\S+)-python(\S+)$", read_dockerfile(), re.MULTILINE)

    assert match is not None
    airflow_version, python_version = match.groups()
    assert airflow_version == pyproject_pins()["apache-airflow"]
    assert read_pyproject()["project"]["requires-python"] == f"=={python_version}.*"


def test_bigquery_client_pin_matches_pyproject():
    match = re.search(r'"google-cloud-bigquery==([^"]+)"', read_dockerfile())

    assert match is not None
    assert match.group(1) == pyproject_pins()["google-cloud-bigquery"]
