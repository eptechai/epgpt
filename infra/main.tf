terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  backend "s3" {}
}

provider "aws" {
  region = var.aws_region
}

resource "local_file" "ssh" {
  content = var.password_ec2
  filename = "${path.module}/connection.pem"
}

resource "aws_instance" "app_server" {
    ami           = "ami-051f8a213df8bc089"  #Amazon Linux 2 AMI (HVM)
    instance_type = "t2.large"

    tags = {
      Name = var.repository_name
      Date = timestamp()
    }

    user_data = <<-EOF
              !/bin/bash
              sudo yum update -y
              sudo yum install docker -y
              sudo service docker start
              sudo usermod -a -G docker ec2-user
              sudo chmod 666 /var/run/docker.sock
              sudo curl -L https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m) -o /usr/local/bin/docker-compose
              sudo chmod +x /usr/local/bin/docker-compose
              sudo aws configure set aws_access_key_id ${var.aws_access_key}
              sudo aws configure set aws_secret_access_key ${var.aws_secret_key}
              sudo aws configure set region ${var.aws_region}
              sudo aws ecr get-login-password --region ${var.aws_region} | docker login --username AWS --password-stdin ${var.docker_url_images}
              docker pull ${var.docker_image_backend}
              docker pull ${var.docker_image_syn}
              sudo systemctl enable docker
              sudo mkdir app
              EOF

    root_block_device {
        volume_size = 30
    }  

    key_name = "connection"
    security_groups =  ["launch-wizard-2"]
}

resource "null_resource" "update-ec2" {
    connection {
      type        = "ssh"
      user        = "ec2-user"
      host        = aws_instance.app_server.public_ip
      private_key = file(local_file.ssh.filename)
    }

    provisioner "remote-exec" {
      inline = [
        "cd ../../app",
        "docker rm $(docker kill $(docker ps -aq))",
        "docker rmi $(docker images -q)",
        "sudo aws ecr get-login-password --region ${var.aws_region} | docker login --username AWS --password-stdin ${var.docker_url_images}",
        "docker pull ${var.docker_image_backend}",
        "docker pull ${var.docker_image_syn}",
        "sudo docker-compose up -d",
      ]
    }

    depends_on = [ local_file.ssh ]
}



output "ec2_ip" {
  value = aws_instance.app_server.public_ip
}