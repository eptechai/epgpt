variable "gcp_project_id" {
  type        = string
  description = "GCP Project ID"
}

variable "vpc" {
  type        = string
  description = "Name of VPC to attach VMs to."
}

variable "subnet" {
  type        = string
  description = "Name of subnet to attach VMs to."
}

variable "region" {
  type        = string
  description = "Name of subnet to attach VMs to."
}

variable "zones" {
    type       = list(string)
    description = "values of zones to attach VMs to. Must have 3 or 5 values."
    validation {
        condition = length(var.zones) == 3 || length(var.zones) == 5
        error_message = "Must have 3 or 5 values."
    }
}