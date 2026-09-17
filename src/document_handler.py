def validate_pdf_upload_contract(event_payload):
    """
    This function is responsible for taking the event_payload.
    Should take the Lambda event metadata for a stored PDF reference and validate that
    the event contains the required S3 location details before downstream processing
    begins. Below are the constraints:

    a) For event_payload accepted values are: a non-empty dictionary representing the
    Lambda event or Step Functions payload. Null, empty, or non-dictionary payloads
    must be rejected.

    b) For S3 reference fields accepted values are: the payload must contain the file
    location needed to retrieve the document from S3, such as bucket and key or the
    project-approved equivalent names. Missing bucket or missing key must be rejected.

    c) For bucket accepted values are: a non-empty string after trimming whitespace.
    Invalid, empty, or non-string bucket values must produce a structured validation
    error.

    d) For key accepted values are: a non-empty string after trimming whitespace.
    The key must point to a PDF object and should therefore end with .pdf when the key
    name is available for validation. Invalid, empty, or non-string key values must be
    rejected.

    e) For validation behavior accepted values are: fail fast on the first violated
    rule, do not continue to downstream functions, and return a structured validation
    outcome that clearly identifies which S3 reference contract check failed.

    The output is: a validated PDF reference structure containing normalized S3 lookup
    fields for downstream processing, and error code.

    Every code should be wrapped under appropriate error/exception handling and the
    error message is to be printed/logged with the error and error code is returned
    along with error message.
    """
    if not isinstance(event_payload, dict) or not event_payload:
        raise ValueError("Event payload must be a non-empty dictionary.")

    s3_reference = event_payload.get("s3")
    if s3_reference is not None and not isinstance(s3_reference, dict):
        raise ValueError("S3 reference must be a dictionary when the 's3' field is used.")

    bucket_value = (
        event_payload.get("bucket")
        or event_payload.get("s3_bucket")
        or event_payload.get("bucket_name")
        or (s3_reference or {}).get("bucket")
    )
    key_value = (
        event_payload.get("key")
        or event_payload.get("s3_key")
        or event_payload.get("object_key")
        or (s3_reference or {}).get("key")
    )

    if not isinstance(bucket_value, str) or not bucket_value.strip():
        raise ValueError("Event payload must include a non-empty S3 bucket value.")

    if not isinstance(key_value, str) or not key_value.strip():
        raise ValueError("Event payload must include a non-empty S3 object key value.")

    bucket_name = bucket_value.strip()
    object_key = key_value.strip()

    if not object_key.lower().endswith(".pdf"):
        raise ValueError("S3 object key must point to a PDF file ending with .pdf.")

    return {
        "bucket": bucket_name,
        "key": object_key,
        "s3_uri": f"s3://{bucket_name}/{object_key}",
    }

def lambda_handler(event, context):
    print("document_handler invoked")
    return {
        "statusCode": 200,
        "body": "Hello from document_handler",
        "event": event,
    }
