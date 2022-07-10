variable "dh_tags" {
  type = map(any)
  default = {
    "dh_platform" = "global-tech"
    "dh_env"      = "production"
    "dh_tribe"    = "developer-platform"
    "dh_squad"    = "platform-techmetrics"
  }
}

variable "ecr-lambda-repo-name" {
  type        = string
  description = "Name of ECR repository for Lambda functions"
  default     = "dh-platform-techm-lambda-repository"
}

variable "docker_tag" {
  description = "The tag of the Docker image"
  type        = string
  default     = "latest"
}
