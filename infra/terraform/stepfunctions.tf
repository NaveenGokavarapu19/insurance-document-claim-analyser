resource "aws_sfn_state_machine" "document_claim_workflow" {
  name     = "${local.resource_prefix}-document-claim-workflow"
  role_arn = aws_iam_role.stepfunctions_execution_role.arn
  type     = "STANDARD"

  definition = jsonencode({
    Comment = "Process uploaded insurance documents through document extraction and summarization."
    StartAt = "ProcessDocument"
    States = {
      ProcessDocument = {
        Type       = "Task"
        Resource   = "arn:aws:states:::lambda:invoke"
        OutputPath = "$.Payload"
        Parameters = {
          FunctionName = aws_lambda_function.document_processor.arn
          Payload = {
            "input.$" = "$"
          }
        }
        Next = "WaitForProcessing"
      }
      WaitForProcessing = {
        Type    = "Wait"
        Seconds = 30
        Next    = "SummarizeDocument"
      }
      SummarizeDocument = {
        Type       = "Task"
        Resource   = "arn:aws:states:::lambda:invoke"
        OutputPath = "$.Payload"
        Parameters = {
          FunctionName = aws_lambda_function.summarizer.arn
          Payload = {
            "input.$" = "$"
          }
        }
        End = true
      }
    }
  })

  tags = local.default_tags

  depends_on = [
    aws_lambda_function.document_processor,
    aws_lambda_function.summarizer,
    aws_iam_role.stepfunctions_execution_role
  ]
}
