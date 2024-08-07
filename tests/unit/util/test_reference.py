from unittest import mock

from virus_clade_utils.util.reference import get_nextclade_dataset


@mock.patch("subprocess.run")
def test_get_nextclade_dataset(tmp_path):
    dataset_path = get_nextclade_dataset("2021-09-01", tmp_path)

    # the dataset_path being returned should contain the correct nextclade
    # datasetset version, as determined by the as_of_date being passed
    # (returned version is temporarily hard-coded until Nextstrain provides the info we need)
    assert "2024-07-17--12-57-03Z" in str(dataset_path)
