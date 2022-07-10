variable "deploy_type" {
  type        = string
  description = "Deploy from file or from container image"
  default     = "Zip"
}

variable "image_uri" {
  type = string
  description = "URI of the Container image in the ECR"
  default = ""
}

variable "base_path" {
  type        = string
  description = "Base path for file operations"
  default     = "../"
}

variable "function_name" {
  type        = string
  description = "Name of Lambda function"
}

variable "source_dir" {
  type        = string
  description = "Source code directory of Lambda function (optional)"
  default     = ""
}

variable "handler" {
  type        = string
  description = "Handler function name of Lambda function (optional)"
  default     = ""
}

variable "runtime" {
  type        = string
  description = "Default runtime for Lambda functions"
  default     = "python3.8"
}

variable "memory" {
  type        = number
  description = "Assigned memory to this Lambda function"
  default     = 512
}

variable "timeout" {
  type        = number
  description = "Timeout in seconds"
  default     = 890
}

variable "lambda_role" {
  type        = string
  description = "Role ARN to assume for executing the Lambda function"
}

variable "layers" {
  type        = list(string)
  description = "List of layers for this Lambda function"
  default = []
}

variable "subnets" {
  type        = list(string)
  description = "List of assigned subnets"
}

variable "security_groups" {
  type        = list(string)
  description = "List of assigned security groups"
}

variable "env_vars" {
  type        = map(string)
  description = "Map of environment variables for this Lambda function"
  default     = {}
}

variable "dh_tags" {
  type        = map(string)
  description = "Map of assigned tags to this Lambda function and related resources"
}

variable "schedule" {
  type        = string
  description = "Schedule expression for Lambda function"
  default     = "rate(1 day)"
}

variable "cloudwatch_prefix" {
  type        = string
  description = "Prefix for CloudWatch Log group"
  default     = "/aws/lambda/"
}

variable "cloudwatch_retention" {
  type        = number
  description = "Retention (in days) for CloudWatch Logs"
  default     = 30
}

variable "ecr_registry" {
  type    = string
  description = "Default ECR registry"
  default = "623160492249.dkr.ecr.eu-central-1.amazonaws.com"
}

variable "ecr_repo_name" {
  type        = string
  description = "ECR repository for Lambda functions"
  default     = "dh-platform-techm-lambda-repository"
}

variable "docker_tag" {
  type        = string
  description = "Default image tag"
  default     = "latest"
}

data "aws_ecr_image" "function_image" {
  repository_name =  var.ecr_repo_name
  image_tag       = "${var.function_name}-${var.docker_tag}"
}

locals {
  source_dir        = length(var.source_dir) == 0 ? "${var.base_path}/lambda/${var.function_name}/" : "${var.base_path}/lambda/${var.source_dir}/"
  handler           = length(var.handler) == 0 ? "lambda_function_${var.function_name}.handler" : "lambda_function_${var.handler}.handler"
  schedule_disabled = (var.schedule == "disabled") ? true : false
  image_tags        = data.aws_ecr_image.function_image.image_tags
  current_image_tag = tolist(setsubtract(local.image_tags, ["latest"]))[0]
  environment_map   = var.env_vars == null ? {} : [var.env_vars]
}

output "lambda_arn" {
  value = aws_lambda_function.lambda_function_container[0].arn
}