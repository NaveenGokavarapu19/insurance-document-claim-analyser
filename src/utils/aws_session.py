from __future__ import annotations

import os
from typing import Any

import boto3

DEFAULT_SESSION_NAME = "insurance-claim-analyser-session"


def _get_current_account_id() -> str | None:
    try:
        sts_client = boto3.client("sts")
        response = sts_client.get_caller_identity()
        return str(response.get("Account"))
    except Exception:
        return None


def _get_current_partition() -> str:
    try:
        sts_client = boto3.client("sts")
        response = sts_client.get_caller_identity()
        caller_arn = response.get("Arn")
        if isinstance(caller_arn, str) and caller_arn.startswith("arn:"):
            return caller_arn.split(":", 2)[1]
    except Exception:
        pass
    return "aws"


def _build_role_arn(role_name: str) -> str:
    if not isinstance(role_name, str) or not role_name.strip():
        raise ValueError("Role name must be a non-empty string.")

    account_id = _get_current_account_id()
    if not account_id:
        raise ValueError("Unable to determine the current AWS account ID.")

    partition = _get_current_partition()
    return f"arn:{partition}:iam::{account_id}:role/{role_name.strip()}"


def _get_current_region() -> str | None:
    configured_region = os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION")
    if configured_region:
        return configured_region

    session = boto3.session.Session()
    return session.region_name


def create_assumed_role_session(
    role_name: str,
    session_name: str = DEFAULT_SESSION_NAME,
    region_name: str | None = None,
    external_id: str | None = None,
) -> boto3.session.Session:
    """Return a boto3 Session using a temporary STS AssumeRole session."""
    if not isinstance(role_name, str) or not role_name.strip():
        raise ValueError("Role name must be a non-empty string.")

    resolved_role_arn = _build_role_arn(role_name)
    current_region = region_name or _get_current_region()

    assume_role_kwargs: dict[str, Any] = {
        "RoleArn": resolved_role_arn,
        "RoleSessionName": session_name or DEFAULT_SESSION_NAME,
    }
    if external_id is not None:
        assume_role_kwargs["ExternalId"] = external_id

    sts_client = boto3.client("sts")
    credentials = sts_client.assume_role(**assume_role_kwargs)["Credentials"]

    return boto3.session.Session(
        aws_access_key_id=credentials["AccessKeyId"],
        aws_secret_access_key=credentials["SecretAccessKey"],
        aws_session_token=credentials["SessionToken"],
        region_name=current_region,
    )


def get_boto3_client(
    service_name: str,
    role_name: str,
    region_name: str | None = None,
    session_name: str = DEFAULT_SESSION_NAME,
    **kwargs: Any,
):
    """Return a boto3 client built from the custom assumed-role session."""
    if not isinstance(service_name, str) or not service_name.strip():
        raise ValueError("Service name must be a non-empty string.")

    custom_session = create_assumed_role_session(
        role_name=role_name,
        session_name=session_name,
        region_name=region_name,
    )
    resolved_region = region_name or custom_session.region_name
    return custom_session.client(service_name.strip(), region_name=resolved_region, **kwargs)


def get_boto3_resource(
    service_name: str,
    role_name: str,
    region_name: str | None = None,
    session_name: str = DEFAULT_SESSION_NAME,
    **kwargs: Any,
):
    """Return a boto3 resource built from the custom assumed-role session."""
    if not isinstance(service_name, str) or not service_name.strip():
        raise ValueError("Service name must be a non-empty string.")

    custom_session = create_assumed_role_session(
        role_name=role_name,
        session_name=session_name,
        region_name=region_name,
    )
    resolved_region = region_name or custom_session.region_name
    return custom_session.resource(service_name.strip(), region_name=resolved_region, **kwargs)
