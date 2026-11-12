# Extends the official image as described in
# https://airflow.apache.org/docs/docker-stack/build.html
# Keep these pins in sync with pyproject.toml (checked by tests/test_docker_pins.py).
FROM apache/airflow:3.3.2-python3.12

# Re-pinning apache-airflow stops pip from upgrading or downgrading Airflow itself.
RUN pip install --no-cache-dir \
    "apache-airflow==${AIRFLOW_VERSION}" \
    "google-cloud-bigquery==3.46.2"
