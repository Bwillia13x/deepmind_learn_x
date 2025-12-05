"""MinIO/S3 storage client."""

from typing import Optional

import boto3
from botocore.exceptions import ClientError

from app.core.config import settings


def get_s3_client():
    """Get S3/MinIO client."""
    return boto3.client(
        "s3",
        endpoint_url=f"http://{settings.minio_endpoint}",
        aws_access_key_id=settings.minio_access_key,
        aws_secret_access_key=settings.minio_secret_key,
    )


def ensure_bucket(name: Optional[str] = None) -> str:
    """Ensure bucket exists, create if not."""
    s3 = get_s3_client()
    bucket = name or settings.minio_bucket
    try:
        s3.head_bucket(Bucket=bucket)
    except ClientError:
        s3.create_bucket(Bucket=bucket)
    return bucket


def upload_file(file_path: str, object_name: str, bucket: Optional[str] = None) -> str:
    """Upload a file to S3/MinIO."""
    s3 = get_s3_client()
    bucket = bucket or settings.minio_bucket
    s3.upload_file(file_path, bucket, object_name)
    return f"s3://{bucket}/{object_name}"


def upload_bytes(data: bytes, object_name: str, bucket: Optional[str] = None) -> str:
    """Upload bytes to S3/MinIO."""
    import io

    s3 = get_s3_client()
    bucket = bucket or settings.minio_bucket
    s3.upload_fileobj(io.BytesIO(data), bucket, object_name)
    return f"s3://{bucket}/{object_name}"


def download_file(object_name: str, file_path: str, bucket: Optional[str] = None) -> None:
    """Download a file from S3/MinIO."""
    s3 = get_s3_client()
    bucket = bucket or settings.minio_bucket
    s3.download_file(bucket, object_name, file_path)


def get_presigned_url(object_name: str, bucket: Optional[str] = None, expires: int = 3600) -> str:
    """Get a presigned URL for an object."""
    s3 = get_s3_client()
    bucket = bucket or settings.minio_bucket
    return s3.generate_presigned_url(
        "get_object",
        Params={"Bucket": bucket, "Key": object_name},
        ExpiresIn=expires,
    )
