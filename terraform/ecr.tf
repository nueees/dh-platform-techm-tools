resource "aws_ecr_repository" "dh-platform-techm-lambda-repository" {
  name = var.ecr-lambda-repo-name

  image_scanning_configuration {
    scan_on_push = true
  }

  tags = var.dh_tags
}

data "aws_ecr_authorization_token" "ecr_token" {
}

data "aws_ecr_authorization_token" "ecr_token_platform_techm_tools" {
  registry_id = "623160492249"
}
