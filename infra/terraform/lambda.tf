resource "aws_cloudwatch_log_group" "document_processor" {
  name              = "/aws/lambda/${local.resource_prefix}-document-processor"
  retention_in_days = 14

  tags = local.default_tags
}

resource "aws_lambda_function" "document_processor" {
  function_name = "${local.resource_prefix}-document-processor"
  role          = aws_iam_role.lambda_execution_role.arn
  handler       = "document_handler.lambda_handler"
  runtime       = "python3.12"
  timeout       = 300
  memory_size   = 512

  s3_bucket = var.s3_bucket_name
  s3_key    = "lambda-artifacts/${var.lambda_code_zip}"

  environment {
    variables = {
      BUCKET_NAME  = var.s3_bucket_name
      PROJECT_NAME = var.project_name
      ENVIRONMENT  = var.environment
    }
  }

  depends_on = [aws_cloudwatch_log_group.document_processor]
}

resource "aws_cloudwatch_log_group" "summarizer" {
  name              = "/aws/lambda/${local.resource_prefix}-summarizer"
  retention_in_days = 14

  tags = local.default_tags
}

resource "aws_lambda_function" "summarizer" {
  function_name = "${local.resource_prefix}-summarizer"
  role          = aws_iam_role.lambda_execution_role.arn
  handler       = "summarizer_handler.lambda_handler"
  runtime       = "python3.12"
  timeout       = 300
  memory_size   = 512

  s3_bucket = var.s3_bucket_name
  s3_key    = "lambda-artifacts/${var.lambda_code_zip}"

  environment {
    variables = {
      BUCKET_NAME  = var.s3_bucket_name
      PROJECT_NAME = var.project_name
      ENVIRONMENT  = var.environment
    }
  }

  depends_on = [aws_cloudwatch_log_group.summarizer]
}
