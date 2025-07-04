# outputs.tf

output "lambda_function_name" {
  description = "The name of the Lambda function."
  value       = aws_lambda_function.crypto_notifier.function_name
}

output "sns_topic_arn" {
  description = "The ARN of the SNS topic for notifications."
  value       = aws_sns_topic.crypto_alerts.arn
}

output "iam_role_arn" {
  description = "The ARN of the IAM role for the Lambda function."
  value       = aws_iam_role.lambda_exec_role.arn
}
