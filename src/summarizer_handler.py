import json
import os

from utils import BedrockClient, create_assumed_role_session, get_current_account_id

MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "amazon.nova-micro-v1:0")
REGION_NAME = os.environ.get("BEDROCK_REGION") or os.environ.get("AWS_REGION") or "us-east-1"


def _invoke_bedrock(prompt):
    """Invoke Bedrock by creating a session first, then injecting it into BedrockClient."""
    role_name = os.environ.get("LAMBDA_EXECUTION_ROLE_NAME")
    if not role_name:
        raise ValueError("LAMBDA_EXECUTION_ROLE_NAME is not configured.")

    account_id = get_current_account_id()
    if not account_id:
        raise ValueError("Unable to resolve the current AWS account ID.")

    session = create_assumed_role_session(
        role_name=role_name,
        account_id=account_id,
        session_name="insurance-claim-analyser-session",
        region_name=REGION_NAME,
    )

    bedrock_client = BedrockClient(
        model_id=MODEL_ID,
        session=session,
        region_name=REGION_NAME,
    )
    result = bedrock_client.converse(prompt=prompt)
    return result.get("text", "")


def lambda_handler(event, context):
    print("summarizer_handler invoked")

    prompt = "Say hello in one sentence."
    try:
        response_text = _invoke_bedrock(prompt)
    except Exception as exc:
        print(f"Bedrock call failed: {exc}")
        response_text = f"Bedrock call failed: {exc}"

    return {
        "statusCode": 200,
        "body": json.dumps({
            "prompt": prompt,
            "model_id": MODEL_ID,
            "response": response_text,
        }),
        "event": event,
    }
