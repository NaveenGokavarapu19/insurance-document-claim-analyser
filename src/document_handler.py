import logging
import tempfile
from pathlib import Path

from utils import get_file_from_s3, pdf_contains_images,load_pdf,extract_tables_from_pdf,parse_claim_tables


logger = logging.getLogger(__name__)


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


    normalized_payload = event_payload.get("input") if isinstance(event_payload.get("input"), dict) else event_payload


    s3_reference = normalized_payload.get("s3")

    bucket_value = (
        normalized_payload.get("bucket")
        or normalized_payload.get("s3_bucket")
        or normalized_payload.get("bucket_name")
        or (s3_reference or {}).get("bucket")
    )
    key_value = (
        normalized_payload.get("key")
        or normalized_payload.get("s3_key")
        or normalized_payload.get("object_key")
        or (s3_reference or {}).get("key")
    )



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
    logger.info("document_handler invoked")
    local_pdf_path: str | None = None

    try:
        validated_pdf_reference = validate_pdf_upload_contract(event)

        with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temporary_pdf_file:
            local_pdf_path = temporary_pdf_file.name

        get_file_from_s3(
            bucket_name=validated_pdf_reference["bucket"],
            s3_key=validated_pdf_reference["key"],
            local_file_path=local_pdf_path,
        )

        pdf_object = load_pdf(local_pdf_path)

        contains_images = pdf_contains_images(pdf_object=pdf_object)
        tables_extracted = extract_tables_from_pdf(pdf_object)
        cleaned_json = parse_claim_tables(tables_extracted)
        claim_information = cleaned_json.get("CLAIM INFORMATION",None)
        policy_holder_information = cleaned_json.get("POLICYHOLDER INFORMATION",None)
        vehicle_information = cleaned_json.get("VEHICLE & INCIDENT DETAILS",None)
        policy_dict = dict()
        policy_dict["claim_number"] = claim_information.get("Claim Number")
        policy_dict["date_filed"] = claim_information.get("Date Filed") 
        policy_dict["date_of_loss"] = claim_information.get("Date of Loss") 
        policy_dict["policy_holder_name"] = policy_holder_information.get("Full Name") 
        policy_dict["policy_holder_address"] = policy_holder_information.get("Address") 
        policy_dict["vehicle_make"] = vehicle_information.get("Vehicle Make") 
        policy_dict["vehicle_model"] = vehicle_information.get("Vehicle Model") 
        policy_dict["vehicle_year"] = vehicle_information.get("Vehicle Year") 
        policy_dict["incident_location"] = vehicle_information.get("Incident Location") 

        return {
            "bucket": validated_pdf_reference["bucket"],
            "key": validated_pdf_reference["key"],
            "s3_uri": validated_pdf_reference["s3_uri"],
            "contains_images": contains_images,
            "policy_details": policy_dict
        }
    except Exception:
        logger.exception("document_handler failed to process the PDF event.")
        raise
    finally:
        if local_pdf_path:
            try:
                Path(local_pdf_path).unlink(missing_ok=True)
            except OSError:
                logger.warning("Unable to remove temporary PDF file: %s", local_pdf_path)
