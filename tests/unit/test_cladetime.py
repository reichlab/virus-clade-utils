from datetime import datetime, timezone

import dateutil.tz
import pytest
from freezegun import freeze_time
from virus_clade_utils.cladetime import CladeTime  # type: ignore
from virus_clade_utils.exceptions import CladeTimeInvalidDateError  # type: ignore


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
