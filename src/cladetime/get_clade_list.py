"""Get a list of SARS-CoV-2 clades."""

import os
from datetime import timedelta

import polars as pl
import structlog
from cloudpathlib import AnyPath

from cladetime.util.config import Config
from cladetime.util.sequence import (
    download_covid_genome_metadata,
    filter_covid_genome_metadata,
    get_clade_counts,
    get_covid_genome_metadata,
)
from cladetime.util.session import _get_session
from cladetime.util.timing import time_function

logger = structlog.get_logger()


@time_function
def get_clades(clade_counts: pl.LazyFrame, threshold: float, threshold_weeks: int, max_clades: int) -> list[str]:
    """Get a list of clades to forecast based."""

    # based on the data's most recent date, get the week start three weeks ago (not including this week)
    max_day = clade_counts.select(pl.max("date")).collect().item()
    threshold_sundays_ago = max_day - timedelta(days=max_day.weekday() + 7 * (threshold_weeks))

    # sum over weeks, combine states, and limit to just the past 3 weeks (not including current week)
    lf = (
        clade_counts.filter(pl.col("date") >= threshold_sundays_ago)
        .sort("date")
        .group_by_dynamic("date", every="1w", start_by="sunday", group_by="clade")
        .agg(pl.col("count").sum())
    )

    # create a separate frame with the total counts per week
    total_counts = lf.group_by("date").agg(pl.col("count").sum().alias("total_count"))

    # join with count data to add a total counts per day column
    prop_dat = lf.join(total_counts, on="date").with_columns(
        (pl.col("count") / pl.col("total_count")).alias("proportion")
    )

    # retrieve list of variants which have crossed the threshold over the past threshold_weeks
    high_prev_variants = prop_dat.filter(pl.col("proportion") > threshold).select("clade").unique().collect()

    # if more than the specified number of clades cross the threshold,
    # take the clades with the largest counts over the past threshold_weeks
    # (if there's a tie, take the first clade alphabetically)
    if len(high_prev_variants) > max_clades:
        high_prev_variants = (
            prop_dat.group_by("clade")
            .agg(pl.col("count").sum())
            .sort("count", "clade", descending=[True, False])
            .collect()
        )

    variants = high_prev_variants.get_column("clade").to_list()[:max_clades]

    return variants


# FIXME: provide ability to instantiate Config for the get_clade_list function and get the data_path from there
def main(
    genome_metadata_bucket: str = Config.nextstrain_ncov_bucket,
    genome_metadata_key: str = Config.nextstrain_genome_metadata_key,
    data_dir: AnyPath = AnyPath(".").home() / "covid_variant",
    threshold: float = 0.01,
    threshold_weeks: int = 3,
    max_clades: int = 9,
) -> list[str]:
    """
    Determine list of clades to model

    Parameters
    ----------
    genome_metadata_bucket : str
        Name of the S3 bucket that hosts Nextstrain's open (GenBank) genome
        metadata files published by the ncov pipeline.
    genome_metdata_key : str
        S3 key of the Nextstrain genome metadata file.
    data_dir : AnyPath
        Path to the location where the genome metadata file is saved after download.
    clade_counts : polars.LazyFrame
        Clade counts by date and location, summarized from Nextstrain metadata
    threshold : float
        Clades that account for at least ``threshold`` proportion of reported
        sequences are candidates for inclusion.
    threshold_weeks : int
        The number of weeks that we look back to identify clades.
    max_clades : int
        The maximum number of clades to include in the list.

    Returns
    -------
    list of strings
    """
    os.makedirs(data_dir, exist_ok=True)
    session = _get_session()
    genome_metadata_path = download_covid_genome_metadata(
        session,
        genome_metadata_bucket,
        genome_metadata_key,
        data_dir,
    )
    lf_metadata = get_covid_genome_metadata(genome_metadata_path)
    lf_metadata_filtered = filter_covid_genome_metadata(lf_metadata)
    counts = get_clade_counts(lf_metadata_filtered)
    clade_list = get_clades(counts, threshold, threshold_weeks, max_clades)

    return clade_list


if __name__ == "__main__":
    main()
