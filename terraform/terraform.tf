terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 3.28.0"
    }

    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 2.16"
    }
  }
  backend "s3" {
    bucket         = "test-platform-techm-tools-lambda"
    key            = "tfstate-techm_tools"
    profile        = "dh-platform-techmetrics-lambda"
    region         = "eu-central-1"
    dynamodb_table = "test-platform-techm-tools-lambda-tf-statelock2"
  }
}

provider "aws" {
  region              = "eu-central-1"
  profile             = "dh-platform-techmetrics-lambda"
  allowed_account_ids = ["623160492249"]
}

provider "docker" {
  registry_auth {
    address  = "${data.aws_caller_identity.current.account_id}.dkr.ecr.eu-central-1.amazonaws.com"
    username = data.aws_ecr_authorization_token.ecr_token.user_name
    password = data.aws_ecr_authorization_token.ecr_token.password
  }
}

data "aws_caller_identity" "current" {}