"""First DAG: proves the image, the mounted ingestion package and the .env settings work."""

from __future__ import annotations

import logging

from airflow.sdk import dag, task

from ingestion.common.config import load_settings

log = logging.getLogger(__name__)


@dag(schedule=None, tags=["smoke-test"], default_args={"retries": 1})
def hello() -> None:
    @task
    def log_project_id() -> None:
        """Load the settings from the environment and log the GCP project id."""
        settings = load_settings()
        log.info("GCP Project ID: %s", settings.gcp_project_id)

    log_project_id()


hello()
