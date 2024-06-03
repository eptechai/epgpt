variable "aws_region" {
    description = "The AWS region to deploy resources"
    type = string
    default = "us-east-1"
}

variable "docker_image_backend" {
    description = "The Docker image to deploy"
    type = string
}

variable "docker_image_syn" {
    description = "The Docker image to deploy"
    type = string
}

variable "docker_url_images" {
    description = "The URL of the Docker image"
    type = string
}

variable "aws_access_key" {
    description = "value of the AWS access key"
    type = string
}

variable "aws_secret_key" {
    description = "value of the AWS secret key"
    type = string
}

variable "password_ec2" {
    description = "password of the EC2 instance"
    type = string
}

variable "repository_name" {
    description = "value of the repository name"
    type = string
}