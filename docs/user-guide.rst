Cladetime
===============


Installing
------------

cladetime can be installed with [pip])(https://pip.pypa.io/): ::

    pip install git+https://github.com/reichlab/cladetime.git


Finding Nextstrain SARS-CoV-2 sequences and sequence metadata
--------------------------------------------------------------

Cladetime provides a CladeTime class that provides a lightweight interface to nextstrain.org files. ::

    from cladetime import CladeTime

    # Instantiating a CladeTime object with no parameters will use the
    # latest available data from nextstrain.org.
    ct = CladeTime()

    # URL to the most recent SARS-CoV-2 sequence file (.fasta)
    ct.url_sequence
    # 'https://nextstrain-data.s3.amazonaws.com/files/ncov/open/sequences.fasta.zst?versionId=d66Hn1T0eFMAg8osEh8Yrod.QEUBRxvu'

    # URL to the metadata that describes the sequences in the above file
    ct.url.sequence_metadata
    # 'https://nextstrain-data.s3.amazonaws.com/files/ncov/open/metadata.tsv.zst?versionId=JTXXFlKyyvt9AerxKMwoZflhFYQFrDek'

    # Metadata about the nextstrain data pipeline that created generated the sequence file and its metadata
    ct.ncov_metadata
    # {'schema_version': 'v1',
    # 'nextclade_version': 'nextclade 3.8.2',
    # 'nextclade_dataset_name': 'SARS-CoV-2',
    # 'nextclade_dataset_version': '2024-09-25--21-50-30Z',
    # 'nextclade_tsv_sha256sum': '5b0f2b64bfe694a3c96bd5a116de8fae23b144bfd3d22da774d4bfe9a84399c3',
    # 'metadata_tsv_sha256sum': '1dc6a4204039e5c69eed84583faf75bbec1629e531dc99aab5bd566d3fb28295'}


Working with SARS-CoV-2 sequence metadata
------------------------------------------

The CladeTime class also provides a Polars LazyFrame object that points to the Nextstrain's sequence metadata file. This file is in .tsv format and contains information about the sequences, such as their collection date, host, and location.

The metadata also includes a clade assignment for each sequence. Nextstrain assigns clades based on a reference tree, and the reference tree varies over time. ::


    import polars as pl
    from cladetime import CladeTime

    ct = CladeTime()

    # ct contains a Polars LazyFrame that references the sequence metadata .tsv file on AWS S3
    lz = ct.sequence_metadata
    lz
    <LazyFrame at 0x105341190>

    # TODO: some polars examples


Time Traveling
--------------

omg!