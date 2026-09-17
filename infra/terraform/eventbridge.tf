resource "aws_s3_bucket_notification" "documents_eventbridge" {
  bucket = var.s3_bucket_name

  eventbridge = true
}

resource "aws_cloudwatch_event_rule" "documents_uploaded" {
  name        = "${local.resource_prefix}-documents-uploaded"
  description = "Start the document claim workflow when a PDF is uploaded under the configured S3 prefix."

  event_pattern = jsonencode({
    source      = ["aws.s3"]
    detail-type = ["Object Created"]
    detail = {
      bucket = {
        name = [var.s3_bucket_name]
      }
      object = {
        key = [{
          prefix = var.s3_documents_prefix
        }]
      }
    }
  })
}

resource "aws_cloudwatch_event_target" "documents_uploaded_workflow" {
  rule     = aws_cloudwatch_event_rule.documents_uploaded.name
  arn      = aws_sfn_state_machine.document_claim_workflow.arn
  role_arn = aws_iam_role.eventbridge_start_stepfunctions_role.arn

  input_transformer {
    input_paths = {
      bucket = "$.detail.bucket.name"
      key    = "$.detail.object.key"
    }

    input_template = <<EOF
{"bucket": <bucket>, "key": <key>}
EOF
  }
}