from __future__ import annotations

import logging
from pathlib import Path
import boto3

logger = logging.getLogger(__name__)


def create_s3_prefix(project_name: str = "", prefix: str = "", object_path: str = "", object_name: str = "") -> str:
    """Join non-empty path components into an S3 object key.

    Components are included in this order: project name, prefix, object path,
    and object name. Empty components are skipped; included values are joined
    with ``/`` and are not otherwise normalized.

    Args:
        project_name: Optional project-level key component.
        prefix: Optional prefix component.
        object_path: Optional intermediate path component.
        object_name: Optional final key component.

    Returns:
        The joined key, or an empty string if every component is empty.
    """
    total_values = (project_name, prefix, object_path, object_name)
    s3_parts_list = [value for value in total_values if value]
    s3_path = "/".join(s3_parts_list)
    print(s3_path)
    return s3_path



def get_file_from_s3(bucket_name: str, s3_key: str, local_file_path: str) -> str:
    """Download an S3 object to a local path and return that path.

    Parent directories are created as needed. Bucket and key values are
    stripped before the boto3 call.

    Args:
        bucket_name: Name of the source S3 bucket.
        s3_key: Key of the object to download.
        local_file_path: Destination filesystem path.

    Returns:
        The destination path as a string.

    Raises:
        ValueError: If a required argument is not a non-empty string.
        FileNotFoundError: If boto3 cannot download the object.
    """
    if not isinstance(bucket_name, str) or not bucket_name.strip():
        raise ValueError("bucket_name must be a non-empty string.")

    if not isinstance(s3_key, str) or not s3_key.strip():
        raise ValueError("s3_key must be a non-empty string.")

    if not isinstance(local_file_path, str) or not local_file_path.strip():
        raise ValueError("local_file_path must be a non-empty string.")

    local_path = Path(local_file_path)
    local_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        s3_client = boto3.client("s3")
        s3_client.download_file(bucket_name.strip(), s3_key.strip(), str(local_path))
        logger.info("Downloaded S3 object %s from bucket %s to %s", s3_key, bucket_name, local_path)
        return str(local_path)
    except Exception as exc:
        logger.exception("Failed to download S3 object %s from bucket %s", s3_key, bucket_name)
        raise FileNotFoundError(f"Unable to download S3 object '{s3_key}' from bucket '{bucket_name}': {exc}") from exc


def read_file(file_path: str) -> str | bytes:
    """Read a local file as UTF-8 text or raw bytes based on its extension.

    Files with ``.txt``, ``.json``, ``.csv``, ``.md``, ``.yaml``, ``.yml``,
    ``.html``, or ``.xml`` extensions are decoded as UTF-8. Other files are
    returned as bytes.

    Args:
        file_path: Path to an existing local file.

    Returns:
        Text for the listed text extensions, otherwise the file's bytes.

    Raises:
        ValueError: If ``file_path`` is not a non-empty string.
        FileNotFoundError: If the path does not exist.
        OSError: If the file cannot be read.
    """
    if not isinstance(file_path, str) or not file_path.strip():
        raise ValueError("file_path must be a non-empty string.")

    local_path = Path(file_path)
    if not local_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        if local_path.suffix.lower() in {".txt", ".json", ".csv", ".md", ".yaml", ".yml", ".html", ".xml"}:
            return local_path.read_text(encoding="utf-8")
        return local_path.read_bytes()
    except Exception as exc:
        logger.exception("Failed to read file %s", file_path)
        raise OSError(f"Unable to read file '{file_path}': {exc}") from exc


def push_file_to_s3(
    file_path: str,
    bucket_name: str,
    prefix: str = "",
    project_name: str = "",
    object_name: str = "",
    object_path: str = "",
) -> str:
    """Upload a local file to S3 and return the generated object key.

    The object key is built from ``project_name``, ``prefix``, ``object_path``,
    and ``object_name`` using :func:`create_s3_prefix`.

    Args:
        file_path: Path to the local file to upload.
        bucket_name: Destination S3 bucket name.
        prefix: Optional key prefix component.
        project_name: Optional project-level key component.
        object_name: Optional final key component.
        object_path: Optional intermediate key path component.

    Returns:
        The generated S3 object key.

    Raises:
        ValueError: If required input is invalid or no object key is generated.
        FileNotFoundError: If ``file_path`` does not exist.
        OSError: If boto3 cannot upload the file.
    """
    if not isinstance(file_path, str) or not file_path.strip():
        raise ValueError("file_path must be a non-empty string.")

    local_path = Path(file_path)
    if not local_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    if not isinstance(bucket_name, str) or not bucket_name.strip():
        raise ValueError("bucket_name must be a non-empty string.")

    object_key = create_s3_prefix(
        prefix=prefix,
        project_name=project_name,
        object_name=object_name,
        object_path=object_path,
    )
    if not object_key:
        raise ValueError("S3 object key could not be generated from the provided path values.")

    try:
        s3_client = boto3.client("s3")
        s3_client.upload_file(str(local_path), bucket_name.strip(), object_key)
        logger.info("Uploaded file %s to S3 bucket %s with key %s", local_path, bucket_name, object_key)
        return object_key
    except Exception as exc:
        logger.exception("Failed to upload file %s to S3 bucket %s", file_path, bucket_name)
        raise OSError(f"Unable to upload file '{file_path}' to bucket '{bucket_name}': {exc}") from exc
