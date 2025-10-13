variable "project_name" {
  description = "Project name"
  default     = "habhub-data-pipeline"
}

variable "vpc" {
  description = "HABhub VPC ID"
  default     = "vpc-04769d5679072de2d"
}

variable "region" {
  description = "The AWS region to create resources in."
  default     = "us-east-1"
}

variable "subnet_pub1" {
  description = "S&E Public Subnet 1"
  default     = "subnet-073cbb5691a961e2a"
}

variable "subnet_pub2" {
  description = "S&E Public Subnet 2"
  default     = "subnet-0739c8eb4c149b506"
}

variable "subnet_prv1" {
  description = "S&E Private Subnet 1"
  default     = "subnet-09951cb214328b219"
}

variable "subnet_prv2" {
  description = "S&E Private Subnet 2"
  default     = "subnet-04dcb4b0fe6271d4b"
}

variable "ecr_root" {
  description = "ECR root url"
  default     = "139464377685.dkr.ecr.us-east-1.amazonaws.com"
}
