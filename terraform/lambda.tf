# Modules for Lambda functions
module "opsgenie_import_bq" {
  source = "../module/lambda_function"

  function_name   = "opsgenie_import_bq"
  schedule        = "cron(0 5 1 * ? *)"
  memory          = 256
  deploy_type     = "Image"
  lambda_role     = aws_iam_role.dh-platform-techm-LambdaExecutionRole.arn
  subnets         = [module.lambdas_vpc.private_subnet_id]
  security_groups = [aws_security_group.allow_outgoing_traffic.id]
  
  dh_tags = var.dh_tags
}
