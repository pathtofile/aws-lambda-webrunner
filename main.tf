# Used to name the various components (SQS Queues, Lambda names, etc.)
variable "base_name" { default = "dothingi" }

# How many and how 'beefy' each lambda should be
variable "lambda_count" { default = 10 }
variable "lambda_timeout_seconds" { default = 60 }
variable "lambda_memory_size" { default = 128 }

# Doing this when lambda_count > 1 dramatically slows
# down provisioning time
variable "enable_input_queue" {
  description = "If set to true, also create input SQS queue"
  type        = bool
  default     = false
}

# ---------------------------------
# ---------------------------------
# Define this block for each region
provider "aws" {
  region = "us-west-1"
  alias  = "us-west-1"
}
module "tf_module_01" {
  source    = "./tf_lambda_sqs"
  providers = { aws = aws.us-west-1 }

  base_name              = var.base_name
  lambda_count           = var.lambda_count
  lambda_timeout_seconds = var.lambda_timeout_seconds
  lambda_memory_size     = var.lambda_memory_size
  enable_input_queue     = var.enable_input_queue
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
#   source    = "./tf_lambda_sqs"
#   providers = { aws = aws.us-east-1 }

#   base_name              = var.base_name
#   lambda_count           = var.lambda_count
#   lambda_timeout_seconds = var.lambda_timeout_seconds
#   lambda_memory_size     = var.lambda_memory_size
#   enable_input_queue     = var.enable_input_queue
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
