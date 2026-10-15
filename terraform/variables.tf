variable "aws_region" {
  type    = string
  default = "ap-south-1"
}
variable "instance_type" {
  type    = string
  default = "t3.small"
}
variable "ssh_allowed_cidr" {
  type        = string
  description = "Your public IP in CIDR notation for SSH, for example 203.0.113.10/32"
}
variable "key_pair_name" {
  type        = string
  description = "Existing EC2 key pair name used for emergency SSH access"
}
