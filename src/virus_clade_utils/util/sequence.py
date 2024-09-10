"""Functions for retrieving and parsing SARS-CoV-2 virus genome data."""

import functools
import json
import lzma
import time
import zipfile
from pathlib import Path

import polars as pl
import structlog
import us
from virus_clade_utils.util.session import check_response, get_session

logger = structlog.get_logger()


def timing(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.perf_counter()
        value = func(*args, **kwargs)
        end_time = time.perf_counter()
        run_time = end_time - start_time
        logger.info(f"{repr(func.__name__)} complete", elapsed_seconds=round(run_time, ndigits=2))
        return value

    return wrapper


def get_covid_genome_data(released_since_date: str, base_url: str, filename: str):
    """
    Download genome data package from NCBI.
    FIXME: Download the Nextclade-processed GenBank sequence data (which originates from NCBI)
    from https://data.nextstrain.org/files/ncov/open/sequences.fasta.zst instead of using
    the NCBI API.
    """
    headers = {
        "Accept": "application/zip",
    }
    session = get_session()
    session.headers.update(headers)

    # TODO: this might be a better as an item in the forthcoming config file
    request_body = {
        "released_since": released_since_date,
        "taxon": "SARS-CoV-2",
        "refseq_only": False,
        "annotated_only": False,
        "host": "Homo sapiens",
        "complete_only": False,
        "table_fields": ["unspecified"],
        "include_sequence": ["GENOME"],
        "aux_report": ["DATASET_REPORT"],
        "format": "tsv",
        "use_psg": False,
    }

    logger.info("NCBI API call starting", released_since_date=released_since_date)

    start = time.perf_counter()
    response = session.post(base_url, data=json.dumps(request_body), timeout=(300, 300))
    check_response(response)

    # Originally tried saving the NCBI package via a stream call and iter_content (to prevent potential
    # memory issues that can arise when download large files). However, ran into an intermittent error:
    # ChunkedEncodingError(ProtocolError('Response ended prematurely').
    # We may need to revisit this at some point, depending on how much data we place to request via the
    # API and what kind of machine the pipeline will run on.
    with open(filename, "wb") as f:
        f.write(response.content)

    end = time.perf_counter()
    elapsed = end - start

    logger.info("NCBI API call completed", elapsed=elapsed)


@timing
def download_nextstrain_file(url: str, data_path: Path, use_existing: bool = False) -> Path:
    """Download genome file from Nextstrain."""

    session = get_session()
    filename = data_path / Path(url).name

    if use_existing and filename.exists():
        logger.info("using existing genome file", genome_file=str(filename))
        return filename

    # 16 MB * 1024 * 1024
    chunk_size_bytes = 16_777_216

    logger.info("Downloading genome file", url=url)

    with session.get(url, stream=True) as result:
        result.raise_for_status()
        with open(filename, "wb") as f:
            for chunk in result.iter_content(chunk_size=chunk_size_bytes):
                f.write(chunk)

    return filename


def get_covid_genome_metadata(metadata_path: Path, num_rows: int | None = None) -> pl.LazyFrame:
    """Read GenBank genome metadata into a Polars LazyFrame."""

    if (compression_type := metadata_path.suffix) in [".tsv", ".zst"]:
        metadata = pl.scan_csv(metadata_path, separator="\t", n_rows=num_rows)
    elif compression_type == ".xz":
        metadata = pl.read_csv(
            lzma.open(metadata_path), separator="\t", n_rows=num_rows, infer_schema_length=100000
        ).lazy()

    return metadata


def filter_covid_genome_metadata(metadata: pl.LazyFrame, cols: list = []) -> pl.LazyFrame:
    """Apply a standard set of filters to the GenBank genome metadata."""

    # Default columns to include in the filtered metadata
    if len(cols) == 0:
        cols = [
            "clade_nextstrain",
            "country",
            "date",
            "division",
            "genbank_accession",
            "genbank_accession_rev",
            "host",
        ]

    # There are some other odd divisions in the data, but these are 50 states and DC
    states = [state.name for state in us.states.STATES]
    states.append("Washington DC")

    # Filter dataset and do some general tidying
    filtered_metadata = (
        metadata.cast({"date": pl.Date}, strict=False)
        .select(cols)
        .filter(
            pl.col("country") == "USA",
            pl.col("division").is_in(states),
            pl.col("date").is_not_null(),
            pl.col("host") == "Homo sapiens",
        )
        .rename({"clade_nextstrain": "clade", "division": "location"})
    )

    return filtered_metadata


def get_clade_counts(filtered_metadata: pl.LazyFrame) -> pl.LazyFrame:
    """Return a count of clades by location and date."""

    cols = [
        "clade",
        "country",
        "date",
        "location",
        "host",
    ]

    counts = filtered_metadata.select(cols).group_by("location", "date", "clade").agg(pl.len().alias("count"))

    return counts


def unzip_sequence_package(filename: str, data_path: str):
    """Unzip the downloaded virus genome data package."""
    with zipfile.ZipFile(filename, "r") as package_zip:
        zip_contents = package_zip.namelist()
        is_metadata = next((s for s in zip_contents if "data_report" in s), None)
        is_sequence = next((s for s in zip_contents if "genomic" in s), None)
        if is_metadata and is_sequence:
            package_zip.extractall(data_path)
        else:
            logger.error("NCBI package is missing expected files", zip_contents=zip_contents)
            # Exit the pipeline without displaying a traceback
            raise SystemExit("Error downloading NCBI package")


def parse_sequence_assignments(df_assignments: pl.DataFrame) -> pl.DataFrame:
    """Parse out the sequence number from the seqName column returned by the clade assignment tool."""

    # polars apparently can't split out the sequence number from that big name column
    # without resorting an apply, so here we're dropping into pandas to do that
    # (might be a premature optimization, since this manoever requires both pandas and pyarrow)
    seq = pl.from_pandas(df_assignments.to_pandas()["seqName"].str.split(" ").str[0].rename("seq"))

    # we're expecting one row per sequence
    if seq.n_unique() != df_assignments.shape[0]:
        raise ValueError("Clade assignment data contains duplicate sequence. Stopping assignment process.")

    # add the parsed sequence number as a new column
    df_assignments = df_assignments.insert_column(1, seq)

    return df_assignments
