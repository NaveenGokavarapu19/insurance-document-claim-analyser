import json
import os

from utils import get_boto3_client

MODEL_ID = os.environ.get("BEDROCK_MODEL_ID", "amazon.nova-micro-v1:0")
REGION_NAME = os.environ.get("BEDROCK_REGION") or os.environ.get("AWS_REGION") or "us-east-1"


def _invoke_bedrock(prompt):
    role_name = os.environ.get("LAMBDA_EXECUTION_ROLE_NAME")
    if not role_name:
        raise ValueError("LAMBDA_EXECUTION_ROLE_NAME is not configured.")

    client = get_boto3_client(
        "bedrock-runtime",
        role_name=role_name,
        region_name=REGION_NAME,
    )

    response = client.converse(
        modelId=MODEL_ID,
        messages=[
            {
                "role": "user",
                "content": [{"text": prompt}],
            }
        ],
    )

    output = response.get("output", {}).get("message", {}).get("content", [])
    return " ".join(item.get("text", "") for item in output if isinstance(item, dict))


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
