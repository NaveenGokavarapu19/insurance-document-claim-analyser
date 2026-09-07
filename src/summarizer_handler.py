def lambda_handler(event, context):
    print("summarizer_handler invoked")
    return {
        "statusCode": 200,
        "body": "Hello from summarizer_handler",
        "event": event,
    }
