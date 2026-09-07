def lambda_handler(event, context):
    print("document_handler invoked")
    return {
        "statusCode": 200,
        "body": "Hello from document_handler",
        "event": event,
    }
