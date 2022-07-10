resource "aws_lambda_function" "lambda_function_container" {
  count            = var.deploy_type == "Image" ? 1 : 0
  package_type     = var.deploy_type
  image_uri       = "${var.ecr_registry}/${var.ecr_repo_name}:${local.current_image_tag}"
  function_name    = var.function_name
  memory_size      = var.memory
  timeout          = var.timeout
  role             = var.lambda_role

  vpc_config {
    subnet_ids         = var.subnets
    security_group_ids = var.security_groups
  }

  environment {
    variables = var.env_vars
  }

  tags = var.dh_tags
}

resource "aws_lambda_function_event_invoke_config" "lambda_function_event_invoke_config" {
  function_name          = var.function_name
  qualifier              = var.deploy_type == "Image" ? aws_lambda_function.lambda_function_container[0].version : aws_lambda_function.lambda_function[0].version
  maximum_retry_attempts = 0
}

resource "aws_cloudwatch_event_rule" "lambda_function_event_rule" {
  count               = local.schedule_disabled ? 0 : 1
  name                = "${var.function_name}_rule"
  description         = "Event rule for ${var.function_name} Lambda function"
  schedule_expression = var.schedule
  tags                = var.dh_tags
}

resource "aws_cloudwatch_event_target" "lambda_function_event_target" {
  count     = local.schedule_disabled ? 0 : 1
  rule      = aws_cloudwatch_event_rule.lambda_function_event_rule[0].name
  target_id = var.function_name
  arn       = var.deploy_type == "Image" ? aws_lambda_function.lambda_function_container[0].arn : aws_lambda_function.lambda_function[0].arn
}

resource "aws_lambda_permission" "lambda_function_permission" {
  count         = local.schedule_disabled ? 0 : 1
  statement_id  = "AllowExecutionFromCloudWatch"
  action        = "lambda:InvokeFunction"
  function_name = var.function_name
  principal     = "events.amazonaws.com"
  source_arn    = aws_cloudwatch_event_rule.lambda_function_event_rule[0].arn
}

resource "aws_cloudwatch_log_group" "lambda_function_log_group" {
  name              = "${var.cloudwatch_prefix}${var.function_name}"
  retention_in_days = var.cloudwatch_retention
  tags              = var.dh_tags
}
