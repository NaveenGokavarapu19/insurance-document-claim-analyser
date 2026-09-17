data "aws_caller_identity" "current" {}

data "aws_iam_policy_document" "lambda_assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

data "aws_iam_policy_document" "lambda_execution" {
  statement {
    sid    = "AllowCloudWatchLogs"
    effect = "Allow"

    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]

    resources = [
      "arn:aws:logs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:log-group:/aws/lambda/${local.resource_prefix}-*",
      "arn:aws:logs:${var.aws_region}:${data.aws_caller_identity.current.account_id}:log-group:/aws/lambda/${local.resource_prefix}-*:log-stream:*"
    ]
  }

  statement {
    sid    = "AllowS3ReadWrite"
    effect = "Allow"

    actions = [
      "s3:GetObject",
      "s3:PutObject",
      "s3:ListBucket"
    ]

    resources = [
      "arn:aws:s3:::${var.s3_bucket_name}",
      "arn:aws:s3:::${var.s3_bucket_name}/*"
    ]
  }

  statement {
    sid    = "AllowBedrockInvoke"
    effect = "Allow"

    actions = [
      "bedrock:InvokeModel",
      "bedrock:InvokeModelWithResponseStream"
    ]

    resources = [
      "arn:aws:bedrock:${var.aws_region}::foundation-model/${var.bedrock_model_id}"
    ]
  }
}

resource "aws_iam_role" "lambda_execution_role" {
  name = var.lambda_execution_role_name

  assume_role_policy = data.aws_iam_policy_document.lambda_assume_role.json

  tags = local.default_tags
}

resource "aws_iam_role_policy" "lambda_execution_policy" {
  name = "${local.resource_prefix}-lambda-policy"
  role = aws_iam_role.lambda_execution_role.id

  policy = data.aws_iam_policy_document.lambda_execution.json
}

data "aws_iam_policy_document" "stepfunctions_assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["states.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

data "aws_iam_policy_document" "stepfunctions_execution" {
  statement {
    sid    = "AllowLambdaInvoke"
    effect = "Allow"

    actions = [
      "lambda:InvokeFunction"
    ]

    resources = ["*"]
  }

  statement {
    sid    = "AllowS3Access"
    effect = "Allow"

    actions = [
      "s3:GetObject",
      "s3:PutObject",
      "s3:ListBucket"
    ]

    resources = [
      "arn:aws:s3:::${var.s3_bucket_name}",
      "arn:aws:s3:::${var.s3_bucket_name}/*"
    ]
  }

}

resource "aws_iam_role" "stepfunctions_execution_role" {
  name = "${local.resource_prefix}-stepfunctions-role"

  assume_role_policy = data.aws_iam_policy_document.stepfunctions_assume_role.json

  tags = local.default_tags
}

resource "aws_iam_role_policy" "stepfunctions_execution_policy" {
  name = "${local.resource_prefix}-stepfunctions-policy"
  role = aws_iam_role.stepfunctions_execution_role.id

  policy = data.aws_iam_policy_document.stepfunctions_execution.json
}

data "aws_iam_policy_document" "eventbridge_assume_role" {
  statement {
    effect = "Allow"

    principals {
      type        = "Service"
      identifiers = ["events.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

data "aws_iam_policy_document" "eventbridge_start_stepfunctions" {
  statement {
    sid    = "AllowStartClaimWorkflow"
    effect = "Allow"

    actions = [
      "states:StartExecution"
    ]

    resources = [
      aws_sfn_state_machine.document_claim_workflow.arn
    ]
  }
}

resource "aws_iam_role" "eventbridge_start_stepfunctions_role" {
  name = "${local.resource_prefix}-eventbridge-stepfunctions-role"

  assume_role_policy = data.aws_iam_policy_document.eventbridge_assume_role.json

  tags = local.default_tags
}

resource "aws_iam_role_policy" "eventbridge_start_stepfunctions_policy" {
  name = "${local.resource_prefix}-eventbridge-stepfunctions-policy"
  role = aws_iam_role.eventbridge_start_stepfunctions_role.id

  policy = data.aws_iam_policy_document.eventbridge_start_stepfunctions.json
}
