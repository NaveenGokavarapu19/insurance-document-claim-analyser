variable "aws_region" {
  description = "AWS region for the insurance claim analyzer infrastructure."
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Short project name used in resource names."
  type        = string
  default     = "insurance-claim-analyzer"
}

variable "environment" {
  description = "Deployment environment name."
  type        = string
  default     = "dev"
}

variable "owner" {
  description = "Owner or team tag for AWS resources."
  type        = string
  default     = "platform"
}

variable "cost_center" {
  description = "Cost center or business unit tag for AWS resources."
  type        = string
  default     = "unknown"
}

variable "s3_bucket_name" {
  description = "Name of the S3 bucket used for document input and output processing."
  type        = string
  default     = "amazon-genai-bucket-naveen"
}

variable "lambda_execution_role_name" {
  description = "Name of the IAM role used by the Lambda execution role."
  type        = string
  default     = "insurance-claim-analyzer-dev-lambda-role"
}

variable "lambda_code_zip" {
  description = "S3 object name for the packaged Lambda code zip used by all Lambda functions."
  type        = string
  default     = "code.zip"
}

variable "bedrock_model_id" {
  description = "Amazon Bedrock model identifier used by the summarizer Lambda."
  type        = string
  default     = "amazon.nova-micro-v1:0"
}

variable "s3_documents_prefix" {
  description = "S3 prefix under which uploaded documents should trigger the Step Functions workflow."
  type        = string
  default     = "resources/documents/"
}
