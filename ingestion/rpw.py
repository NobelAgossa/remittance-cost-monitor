"""World Bank Remittance Prices Worldwide (RPW) quarterly files (implemented in week 4).

Files are downloaded manually from the RPW website into `data/landing/rpw/`
(git-ignored). The expected columns are defined by the data contract written in week 2.
"""

from __future__ import annotations

from pathlib import Path


def load_rpw_file(path: Path) -> None:
    """Validate an RPW file and load it into its quarter partition.

    Validates the file against the data contract, normalizes column names, derives the
    quarter, writes a clean file and loads it into the quarter partition of
    `raw.rpw_prices` with WRITE_TRUNCATE. An invalid file fails with a message listing
    every problem found.
    """
    raise NotImplementedError("RPW ingestion is implemented in week 4 (see docs/PLAN.md).")
