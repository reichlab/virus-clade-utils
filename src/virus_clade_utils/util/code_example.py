from datetime import datetime

from virus_clade_utils.util.config import Config
from virus_clade_utils.util.sequence import download_covid_genome_metadata

# sequence_date and reference_tree_as_of are not needed, but they're
# required to for creating a Config instance (needs a refactor)
sequence_date = reference_tree_as_of = datetime.now()
config = Config(sequence_date, reference_tree_as_of)
bucket = Config.nextstrain_ncov_bucket
key = Config.nextstrain_genome_metadata_key

metadata = download_covid_genome_metadata(
    bucket,
    key,
    config.data_path,
    # download the S3 file as of the date below (YYYY-MM-DD)
    # remove if you want the latest file
    as_of="2024-09-24",
    # if the file for above date already exists, don't re-download
    use_existing=True,
)
