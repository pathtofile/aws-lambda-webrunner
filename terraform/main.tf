# Variables
variable "location" { default = "us-west-1" }

# Provider
provider "aws" {
  region = var.location
  default_tags {
    tags = {
      environment = "dothingi"
    }
  }
}
