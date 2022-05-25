terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "> 1.0"
    }
  }
}

# Used when we need to reference the name of
# the current region
data "aws_region" "current" {}
output "aws_region" { value = data.aws_region.current.name }
