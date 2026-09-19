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


def get_current_account_id() -> str | None:
    """Return the active AWS account ID for the current execution context."""
    return _get_current_account_id()


def _get_current_region() -> str | None:
    configured_region = os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION")
    if configured_region:
        return configured_region

    session = boto3.session.Session()
    return session.region_name


def _is_same_account_and_region(account_id: str, region_name: str | None) -> bool:
    if not isinstance(account_id, str) or not account_id.strip():
        return False

    current_account_id = _get_current_account_id()
    if not current_account_id:
        return False

    current_region = _get_current_region()
    target_region = region_name or current_region
    return account_id.strip() == current_account_id.strip() and target_region == current_region


def create_assumed_role_session(
    role_name: str,
    account_id: str,
    session_name: str = DEFAULT_SESSION_NAME,
    region_name: str | None = None,
    external_id: str | None = None,
) -> boto3.session.Session:
    """Return a boto3 Session using a temporary STS AssumeRole session for cross-account work."""
    if not isinstance(role_name, str) or not role_name.strip():
        raise ValueError("Role name must be a non-empty string.")
    if not isinstance(account_id, str) or not account_id.strip():
        raise ValueError("Account ID must be provided explicitly for the target role.")

    current_region = region_name or _get_current_region()
    if _is_same_account_and_region(account_id, current_region):
        return boto3.session.Session(region_name=current_region)

    assume_role_kwargs: dict[str, Any] = {
        "RoleArn": f"arn:{os.environ.get('AWS_PARTITION', 'aws')}:iam::{account_id.strip()}:role/{role_name.strip()}",
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
    account_id: str,
    region_name: str | None = None,
    session_name: str = DEFAULT_SESSION_NAME,
    **kwargs: Any,
):
    """Return a boto3 client built from the active session or a temporary assumed-role session."""
    if not isinstance(service_name, str) or not service_name.strip():
        raise ValueError("Service name must be a non-empty string.")

    custom_session = create_assumed_role_session(
        role_name=role_name,
        account_id=account_id,
        session_name=session_name,
        region_name=region_name,
    )
    resolved_region = region_name or custom_session.region_name
    return custom_session.client(service_name.strip(), region_name=resolved_region, **kwargs)


def get_boto3_resource(
    service_name: str,
    role_name: str,
    account_id: str,
    region_name: str | None = None,
    session_name: str = DEFAULT_SESSION_NAME,
    **kwargs: Any,
):
    """Return a boto3 resource built from the active session or a temporary assumed-role session."""
    if not isinstance(service_name, str) or not service_name.strip():
        raise ValueError("Service name must be a non-empty string.")

    custom_session = create_assumed_role_session(
        role_name=role_name,
        account_id=account_id,
        session_name=session_name,
        region_name=region_name,
    )
    resolved_region = region_name or custom_session.region_name
    return custom_session.resource(service_name.strip(), region_name=resolved_region, **kwargs)
