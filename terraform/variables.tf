# Used to name the various components (SQS Queues, Lambda names, etc.)
variable "base_name" { default = "dothingi" }

# How many and how 'beefy' each lambda should be
variable "lambda_count" { default = 1 }
variable "lambda_timeout_seconds" { default = 60 }
variable "lambda_memory_size" { default = 128 }

# Doing this when lambda_count > 1 dramatically slows
# down provisioning time
variable "enable_input_queue" {
  description = "If set to true, also create input SQS queue"
  type        = bool
  default     = true
}
