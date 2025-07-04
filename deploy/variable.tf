# variables.tf

variable "aws_region" {
  description = "The AWS region to deploy resources in."
  type        = string
  default     = "us-east-1"
}

variable "notification_email" {
  description = "The email address to send notifications to."
  type        = string
  # You must provide a value for this variable
}
