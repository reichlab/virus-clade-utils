import boto3
import pytest
import requests
from freezegun import freeze_time
from moto import mock_aws


@pytest.fixture
def mock_session(mocker):
    """Session mock for testing functions that use requests.Session"""
    mock_session = mocker.patch.object(requests, "Session", autospec=True)
    mock_session.return_value.__enter__.return_value = mock_session
    return mock_session


@pytest.fixture
def s3_setup():
    """Setup mock S3 bucket with versioned objects."""
    with mock_aws():
        bucket_name = "versioned-bucket"
        object_key = "metadata/object-key/metadata.tsv.zst"

        s3_client = boto3.client("s3", region_name="us-east-1")
        s3_client.create_bucket(Bucket=bucket_name)
        s3_client.put_bucket_versioning(Bucket=bucket_name, VersioningConfiguration={"Status": "Enabled"})

        # Upload multiple versions of the object
        versions = [
            ("2023-01-01 03:05:01", "object version 1"),
            ("2023-02-05 14:33:06", "object version 2"),
            ("2023-03-22 22:55:12", "object version 3"),
        ]

        for version_date, content in versions:
            # use freezegun to override system date, which in
            # turn sets S3 object version LastModified date
            with freeze_time(version_date):
                s3_client.put_object(
                    Bucket=bucket_name,
                    Key=object_key,
                    Body=content,
                )
        yield s3_client, bucket_name, object_key
