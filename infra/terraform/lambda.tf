locals {
  # Goes up two levels (from infra/terraform to project root), then into layers/
  layer_zip_path = "${path.module}/../../layers/pdf_layer.zip"
}

resource "aws_s3_object" "pdf_layer_zip" {
  bucket = var.s3_bucket_name
  key    = "lambda-layers/${var.pdf_layer_layer_zip_name}"
  source = local.layer_zip_path
  etag   = filemd5(local.layer_zip_path)
}

resource "aws_lambda_layer_version" "pdf_layer" {
  layer_name               = "pdf_layer"
  description              = "Python 3.12 PDF and Pillow dependencies"
  s3_bucket                = aws_s3_object.pdf_layer_zip.bucket
  s3_key                   = aws_s3_object.pdf_layer_zip.key
  s3_object_version        = aws_s3_object.pdf_layer_zip.version_id
  compatible_runtimes      = ["python3.12"]
  compatible_architectures = ["x86_64"] # Match --platform=linux/amd64 from Dockerfile

  # Publishes a new layer version whenever the zip content changes
  source_code_hash = filebase64sha256(local.layer_zip_path)
}


data "archive_file" "lambda_code_zip" {
  type        = "zip"
  source_dir  = "${path.module}/../../src"
  output_path = "${path.module}/${var.lambda_code_zip}"
}

resource "aws_s3_object" "lambda_code_zip" {
  bucket = var.s3_bucket_name
  key    = "lambda-artifacts/${var.lambda_code_zip}"
  source = data.archive_file.lambda_code_zip.output_path
  etag   = filemd5(data.archive_file.lambda_code_zip.output_path)
}

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

  s3_bucket        = var.s3_bucket_name
  s3_key           = "lambda-artifacts/${var.lambda_code_zip}"
  source_code_hash = data.archive_file.lambda_code_zip.output_base64sha256

  layers = [
    aws_lambda_layer_version.pdf_layer.arn
    ]


  environment {
    variables = {
      BUCKET_NAME                = var.s3_bucket_name
      PROJECT_NAME               = var.project_name
      ENVIRONMENT                = var.environment
      LAMBDA_EXECUTION_ROLE_NAME = var.lambda_execution_role_name
    }
  }

  depends_on = [
    aws_cloudwatch_log_group.document_processor,
    aws_s3_object.lambda_code_zip
  ]
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

  s3_bucket        = var.s3_bucket_name
  s3_key           = "lambda-artifacts/${var.lambda_code_zip}"
  source_code_hash = data.archive_file.lambda_code_zip.output_base64sha256

  layers = [
    aws_lambda_layer_version.pdf_layer.arn
  ]

  environment {
    variables = {
      BUCKET_NAME                = var.s3_bucket_name
      PREFIX                     = var.prefix
      PROJECT_NAME               = var.project_name
      OBJECT_PATH                = var.object_path
      ENVIRONMENT                = var.environment
      LAMBDA_EXECUTION_ROLE_NAME = var.lambda_execution_role_name
      BEDROCK_MODEL_ID           = var.bedrock_model_id
      BEDROCK_REGION             = var.aws_region
    }
  }

  depends_on = [
    aws_cloudwatch_log_group.summarizer,
    aws_s3_object.lambda_code_zip
  ]
}
