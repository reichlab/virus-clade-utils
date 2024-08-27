"""Functions for retrieving and parsing SARS-CoV-2 phylogenic tree data."""

import subprocess
from pathlib import Path

import structlog

logger = structlog.get_logger()


def get_nextclade_dataset(as_of_date: str, data_path_root: str) -> str:
    """
    Return the Nextclade dataset relevant to a specified as_of_date. The dataset is
    in .zip format and contains two components required for assignming virus
    genome sequences to clades: a tree and the reference sequence of the virus.
    """

    # Until Nextstrain provides this information, we're hard-coding a
    # a specific version of the nextclade dataset here.
    as_of_date = "not yet implemented"
    DATASET_VERSION = "2024-07-17--12-57-03Z"
    DATASET_PATH = Path(f"{data_path_root}/nextclade_dataset_{DATASET_VERSION}.zip")

    subprocess.run(
        [
            "nextclade",
            "dataset",
            "get",
            "--name",
            "sars-cov-2",
            "--tag",
            DATASET_VERSION,
            "--output-zip",
            str(DATASET_PATH),
        ]
    )

    logger.info(
        "Nextclade reference dataset retrieved", as_of_date=as_of_date, version=DATASET_VERSION, output_zip=DATASET_PATH
    )

    return DATASET_PATH
