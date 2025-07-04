# main.tf

# Configure the AWS Provider
provider "aws" {
  region = var.aws_region
}

# --- IAM ---

# IAM Role for the Lambda function
resource "aws_iam_role" "lambda_exec_role" {
  name = "CryptoNotifierLambdaRole"

  assume_role_policy = jsonencode({
    Version   = "2012-10-17",
    Statement = [
      {
        Action    = "sts:AssumeRole",
        Effect    = "Allow",
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# IAM Policy with necessary permissions
resource "aws_iam_policy" "lambda_policy" {
  name        = "CryptoNotifierLambdaPolicy"
  description = "Policy for Crypto Notifier Lambda function"

  policy = jsonencode({
    Version   = "2012-10-17",
    Statement = [
      {
        Action   = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ],
        Effect   = "Allow",
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Action   = "sns:Publish",
        Effect   = "Allow",
        Resource = aws_sns_topic.crypto_alerts.arn
      },
      {
        Action   = [
          "ssm:GetParameter",
          "ssm:PutParameter"
        ],
        Effect   = "Allow",
        Resource = "arn:aws:ssm:${var.aws_region}:${data.aws_caller_identity.current.account_id}:parameter/CryptoLastPrices"
      },
      {
        Action = [
            "secretsmanager:GetSecretValue"
        ],
        Effect = "Allow",
        Resource = aws_secretsmanager_secret.binance_keys.arn
      }
    ]
  })
}

# Attach the policy to the role
resource "aws_iam_role_policy_attachment" "lambda_policy_attach" {
  role       = aws_iam_role.lambda_exec_role.name
  policy_arn = aws_iam_policy.lambda_policy.arn
}

# --- SNS ---

# SNS Topic for sending notifications
resource "aws_sns_topic" "crypto_alerts" {
  name = "CryptoPriceAlerts"
}

# SNS Subscription (e.g., email)
resource "aws_sns_topic_subscription" "email_subscription" {
  topic_arn = aws_sns_topic.crypto_alerts.arn
  protocol  = "email"
  endpoint  = var.notification_email
}

# --- Lambda ---

# Data source to get current AWS account ID
data "aws_caller_identity" "current" {}

# Lambda Function
resource "aws_lambda_function" "crypto_notifier" {
  filename      = "lambda_function.zip"
  function_name = "CryptoPriceMonitor"
  role          = aws_iam_role.lambda_exec_role.arn
  handler       = "crypto_notifier_lambda.lambda_handler" # Corresponds to filename.function_name
  runtime       = "python3.9"
  source_code_hash = filebase64sha256("lambda_function.zip")


  environment {
    variables = {
      SNS_TOPIC_ARN = aws_sns_topic.crypto_alerts.arn
    }
  }
}

# --- EventBridge (CloudWatch Events) ---

# EventBridge rule to trigger the Lambda function every hour
resource "aws_cloudwatch_event_rule" "every_hour" {
  name                = "RunCryptoNotifierEveryHour"
  description         = "Fires every hour"
  schedule_expression = "rate(1 hour)"
}

# Target for the EventBridge rule (the Lambda function)
resource "aws_cloudwatch_event_target" "lambda_target" {
  rule      = aws_cloudwatch_event_rule.every_hour.name
  target_id = "CryptoNotifierLambda"
  arn       = aws_lambda_function.crypto_notifier.arn
}

# Permission for EventBridge to invoke the Lambda function
resource "aws_lambda_permission" "allow_cloudwatch" {
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.crypto_notifier.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.every_hour.arn
}

# --- SSM Parameter Store ---
resource "aws_ssm_parameter" "last_prices" {
  name  = "CryptoLastPrices"
  type  = "String"
  value = "{}" # Initial empty value
}

# --- (Optional) Secrets Manager ---
resource "aws_secretsmanager_secret" "binance_keys" {
  name = "BinanceApiKeys"
}

resource "aws_secretsmanager_secret_version" "binance_keys_version" {
  secret_id = aws_secretsmanager_secret.binance_keys.id
  secret_string = jsonencode({
    BINANCE_API_KEY    = "YOUR_API_KEY"
    BINANCE_SECRET_KEY = "YOUR_SECRET_KEY"
  })
}
