module "lambdas_vpc" {
  source = "github.com/kierancrown/terraform-lambda-fixed-ip"
  region = "eu-central-1"
}

resource "aws_security_group" "allow_outgoing_traffic" {
  name        = "AWS_Lambda_SG"
  description = "AWS_Lambda_VPN"
  vpc_id      = module.lambdas_vpc.vpc_id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
  tags = var.dh_tags

}
