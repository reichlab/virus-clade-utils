from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from virus_clade_utils.get_clade_list import main


@pytest.fixture
def test_file_path() -> Path:
    """
    Return path to the unit test files.
    """
    test_file_path = Path(__file__).parents[1].joinpath("data")
    return test_file_path


@pytest.mark.parametrize(
    "threshold, weeks, max_clades, expected_list",
    [
        (0.1, 3, 9, ["AA", "AA.ZZ", "BB", "CC", "DD", "EE", "FF"]),
        (0.3, 3, 9, ["AA", "AA.ZZ", "EE"]),
        (0.1, 2, 9, ["AA.ZZ", "AA", "BB", "CC", "DD", "EE", "FF"]),
        (0.1, 1, 9, ["AA", "BB", "CC", "FF"]),
        (0.3, 1, 9, ["AA"]),
        (0.1, 3, 4, ["AA", "AA.ZZ", "BB", "CC"]),
        (0.3, 3, 2, ["AA", "AA.ZZ"]),
        (0.1, 2, 3, ["AA", "BB", "CC"]),
        (0.1, 1, 3, ["AA", "BB", "CC"]),
        (1, 3, 9, []),
    ],
)
def test_clade_list(test_file_path, tmp_path, threshold, weeks, max_clades, expected_list):
    test_genome_metadata = test_file_path / "test_metadata.tsv"
    mock = MagicMock(return_value=test_genome_metadata, name="genome_metadata_download_mock")

    with patch("virus_clade_utils.get_clade_list.download_nextstrain_file", mock):
        actual_list = main(test_genome_metadata, tmp_path, threshold, weeks, max_clades)

    assert set(expected_list) == set(actual_list)
