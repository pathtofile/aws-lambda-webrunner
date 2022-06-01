# ---------------------------------
# ---------------------------------
# Define this block for each region
provider "aws" {
  region = "us-west-1"
  alias  = "us-west-1"
}
module "tf_module_01" {
  source = "./lambda-sqs"
  providers = {
    aws = aws.us-west-1
  }
}
# ---------------------------------
# ---------------------------------

# ---------------------------------
# ---------------------------------
# provider "aws" {
#   region = "us-east-1"
#   alias  = "us-east-1"
# }
# module "tf_module_02" {
#   source = "./lambda-sqs"
#   providers = {
#     aws = aws.us-east-1
#   }
# }
# ---------------------------------
# ---------------------------------


# Output URLS
# MAKE SURE you add each region to
# the "modules" local variable below:
locals {
  modules = toset([
    module.tf_module_01,
    # module.tf_module_02,
  ])
}

output "config" {
  value = local.modules[*].config
}
