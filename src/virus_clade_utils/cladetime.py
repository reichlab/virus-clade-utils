"""Class for clade time traveling."""

from datetime import datetime, timezone

import structlog

from virus_clade_utils.exceptions import CladeTimeInvalidDateError
from virus_clade_utils.util.config import Config
from virus_clade_utils.util.reference import _get_s3_object_url
from virus_clade_utils.util.sequence import _get_ncov_metadata

logger = structlog.get_logger()


class CladeTime:
    """
    Wrapper around Nextstrain/Nextclade tooling to generate Sars-CoV-2 genome clade assignments
    and aggregations at a specific point in time. CladeTime operates on Genbank sequences.

    Attributes
    ----------
    sequence_as_of : datetime
        Use the NextStrain sequences and sequence metadata that were available
        as of this date and time (UTC).
    ncov_metadata : dict
        Metadata for the Nextstrain ncov pipeline that generated the sequence and
        sequence metadata that correspond to the sequence_as_of date.
    tree_as_of : datetime
        Use the NextStrain reference tree that was available as of this
        date and time (UTC).
        Can be a datetime object, a string in the format
        "YYYY-MM-DD", or None (which defaults to the current date and time).
    url_ncov_metadata: str
        S3 URL to the Nextstrain ncov metadata file (.json)
    url_sequence : str
        S3 URL to the Nextstrain Sars-CoV-2 sequence file (zst-compressed
        .fasta) that was available at the sequence_as_of.
    url_sequence_metadata : str
        S3 URL to the Nextstrain Sars-CoV-2 sequence metadata file
        (zst-compressed tsv) that was available at the sequence_as_of.
    """

    def __init__(self, sequence_as_of=None, tree_as_of=None):
        """
        Parameters
        ----------
        sequence_as_of : datetime | str | None, default = now()
            Use the NextStrain sequences and sequence metadata that were available
            as of this date. Can be a datetime object, a string in the format
            "YYYY-MM-DD", or None (which defaults to the current date and time).
        tree_as_of : datetime | str | None, default = now()
            Use the NextStrain reference tree that was available as of this date.
            Can be a datetime object, a string in the format
            "YYYY-MM-DD", or None (which defaults to the current date and time).
        """

        self._config = self._get_config()
        self.sequence_as_of = self._validate_as_of_date(sequence_as_of)
        self.tree_as_of = self._validate_as_of_date(tree_as_of)
        self._ncov_metadata = {}

        self.url_sequence = _get_s3_object_url(
            self._config.nextstrain_ncov_bucket, self._config.nextstrain_genome_sequence_key, self.sequence_as_of
        )[1]
        self.url_sequence_metadata = _get_s3_object_url(
            self._config.nextstrain_ncov_bucket, self._config.nextstrain_genome_metadata_key, self.sequence_as_of
        )[1]

        # Nextstrain began publishing ncov pipeline metadata starting on 2024-08-01
        if self.sequence_as_of >= self._config.nextstrain_min_ncov_metadata_date:
            self.url_ncov_metadata = _get_s3_object_url(
                self._config.nextstrain_ncov_bucket, self._config.nextstrain_ncov_metadata_key, self.sequence_as_of
            )[1]
        else:
            self.url_ncov_metadata = None

    @property
    def ncov_metadata(self):
        return self._ncov_metadata

    @ncov_metadata.getter
    def ncov_metadata(self) -> dict:
        """Set the ncov_metadata attribute."""
        if self.url_ncov_metadata:
            metadata = _get_ncov_metadata(self.url_ncov_metadata)
            return metadata
        else:
            metadata = {}
        return metadata

    def _get_config(self) -> Config:
        """Return a config object."""
        # dates passed to Config don't actually do anything in this case
        # (config needs a refactor)
        config = Config(datetime.now(), datetime.now())

        return config

    def _validate_as_of_date(self, as_of: str) -> datetime:
        """Validate date the as_of dates used to instantiate CladeTime."""
        if as_of is None:
            as_of_date = datetime.now()
        elif isinstance(as_of, datetime):
            as_of_date = as_of
        elif isinstance(as_of, str):
            try:
                as_of_date = datetime.strptime(as_of, "%Y-%m-%d")
            except ValueError as e:
                raise CladeTimeInvalidDateError(f"Invalid date string: {as_of} (should be in YYYY-MM-DD format)") from e

        as_of_date = as_of_date.replace(microsecond=0, tzinfo=timezone.utc)
        if as_of_date < self._config.nextstrain_min_seq_date:
            raise CladeTimeInvalidDateError(f"Date must be after May 1, 2023: {as_of_date}")

        if as_of_date > datetime.now().replace(tzinfo=timezone.utc):
            raise CladeTimeInvalidDateError(f"Date cannot be in the future: {as_of_date}")

        return as_of_date
