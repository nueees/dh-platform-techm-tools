# IAM & Policy
data "aws_iam_policy_document" "dh-platform-techm-LambdaExecutionAssumeRolePolicyDocument" {
  statement {
    actions = ["sts:AssumeRole"]
    effect  = "Allow"

    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

data "aws_iam_policy_document" "dh-platform-techm-LambdaExecutionRolePolicyDocument" {
  statement {
    actions = ["logs:CreateLogGroup",
        "ec2:DescribeNetworkInterfaces",
        "ec2:CreateNetworkInterface",
        "ec2:DeleteNetworkInterface",
        "ec2:DescribeInstances",
        "ec2:AttachNetworkInterface",
        "ec2:AWSLambdaVPCAccessExecutionRole",
        "logs:CreateLogStream",
        "logs:PutLogEvents",
        "ssm:GetParameter",
        "s3:*",
        "sts:AssumeRole"]
    effect    = "Allow"
    resources = ["*"]
  }
}

resource "aws_iam_policy" "dh-platform-techm-LambdaExecutionRolePolicy" {
  name     = "dh-platform-techm-LambdaExecutionRolePolicy"
  policy   = data.aws_iam_policy_document.dh-platform-techm-LambdaExecutionRolePolicyDocument.json
}

resource "aws_iam_role" "dh-platform-techm-LambdaExecutionRole" {
  name               = "dh-platform-techm-LambdaExecutionRole"
  assume_role_policy = data.aws_iam_policy_document.dh-platform-techm-LambdaExecutionAssumeRolePolicyDocument.json
}

resource "aws_iam_role_policy_attachment" "dh-platform-techm-LambdaExecutionRolePolicyAttachment" {
  role       = aws_iam_role.dh-platform-techm-LambdaExecutionRole.name
  policy_arn = aws_iam_policy.dh-platform-techm-LambdaExecutionRolePolicy.arn
}