from datetime import datetime, timezone
from unittest.mock import MagicMock, patch
from urllib.parse import parse_qs, urlparse

import dateutil.tz
import pytest
from freezegun import freeze_time
from virus_clade_utils.cladetime import CladeTime
from virus_clade_utils.exceptions import CladeTimeInvalidDateError
from virus_clade_utils.util.config import Config


def test_cladetime_no_args():
    with freeze_time("2024-12-13 16:21:34", tz_offset=-4):
        ct = CladeTime()
        expected_date = datetime.now(timezone.utc)
    assert ct.tree_as_of == expected_date
    assert ct.sequence_as_of == expected_date


@pytest.mark.parametrize(
    "sequence_as_of, tree_as_of, expected_sequence_as_of, expected_tree_as_of",
    [
        (
            "2024-09-01",
            "2024-01-01",
            datetime(2024, 9, 1, tzinfo=timezone.utc),
            datetime(2024, 1, 1, tzinfo=timezone.utc),
        ),
        (
            None,
            "2023-12-21",
            datetime(2025, 7, 13, 16, 21, 34, tzinfo=timezone.utc),
            datetime(2023, 12, 21, tzinfo=timezone.utc),
        ),
        (
            datetime(2024, 9, 30, 18, 24, 59, 655398),
            None,
            datetime(2024, 9, 30, 18, 24, 59, tzinfo=timezone.utc),
            datetime(2025, 7, 13, 16, 21, 34, tzinfo=timezone.utc),
        ),
        (
            datetime(2024, 2, 22, 22, 22, 22, 222222, tzinfo=dateutil.tz.gettz("US/Eastern")),
            datetime(2024, 2, 22, tzinfo=dateutil.tz.gettz("US/Eastern")),
            datetime(2024, 2, 22, 22, 22, 22, tzinfo=timezone.utc),
            datetime(2024, 2, 22, tzinfo=timezone.utc),
        ),
    ],
)
def test_cladetime_as_of_dates(sequence_as_of, tree_as_of, expected_sequence_as_of, expected_tree_as_of):
    with freeze_time("2025-07-13 16:21:34"):
        ct = CladeTime(sequence_as_of=sequence_as_of, tree_as_of=tree_as_of)

    assert ct.sequence_as_of == expected_sequence_as_of
    assert ct.tree_as_of == expected_tree_as_of


@pytest.mark.parametrize("bad_date", ["2020-07-13", "2022-12-32", "2063-04-05"])
def test_cladetime_invalid_date(bad_date):
    with pytest.raises(CladeTimeInvalidDateError):
        CladeTime(sequence_as_of=bad_date, tree_as_of=bad_date)


@pytest.mark.parametrize(
    "sequence_as_of, expected_content",
    [
        (
            "2024-09-01",
            "version 4",
        ),
        (
            None,
            "version 4",
        ),
        (
            datetime(2023, 2, 5, 5, 55),
            "version 2",
        ),
        (
            datetime(2023, 2, 5, 1, 22),
            "version 1",
        ),
    ],
)
def test_cladetime_urls(s3_setup, sequence_as_of, expected_content):
    s3_client, bucket_name, s3_object_keys = s3_setup

    # FIXME: perhaps the test_config that works with the mock aws setup
    # should be a fixture.
    test_config = Config(datetime.now(), datetime.now())
    test_config.nextstrain_min_seq_date = datetime(2023, 1, 1).replace(tzinfo=timezone.utc)
    test_config.nextstrain_ncov_bucket = "versioned-bucket"
    test_config.nextstrain_genome_metadata_key = s3_object_keys["sequence_metadata"]
    test_config.nextstrain_genome_sequence_key = s3_object_keys["sequence"]
    test_config.nextstrain_ncov_metadata_key = s3_object_keys["ncov_metadata"]
    mock = MagicMock(return_value=test_config, name="CladeTime._get_config_mock")

    with patch("virus_clade_utils.cladetime.CladeTime._get_config", mock):
        with freeze_time("2024-09-02 00:00:00"):
            ct = CladeTime(sequence_as_of=sequence_as_of)
            for url in [ct.url_sequence, ct.url_sequence_metadata]:
                parsed_url = urlparse(url)
                key = parsed_url.path.strip("/")
                version_id = parse_qs(parsed_url.query)["versionId"][0]
                object = s3_client.get_object(Bucket=bucket_name, Key=key, VersionId=version_id)
                assert expected_content in object["Body"].read().decode("utf-8").lower()

            if ct.sequence_as_of < test_config.nextstrain_min_ncov_metadata_date:
                assert ct.url_ncov_metadata is None
            else:
                assert ct.url_ncov_metadata is not None
