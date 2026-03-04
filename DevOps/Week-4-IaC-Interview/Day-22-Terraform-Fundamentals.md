# Day 22: Terraform Fundamentals – Infrastructure as Code

## 📚 Topics to Cover (3-4 hours)

---

## 1. What is Infrastructure as Code?

| Approach | Tools | Style |
|----------|-------|-------|
| **Declarative** | Terraform, CloudFormation, Pulumi | Define desired state |
| **Imperative** | Ansible, Shell scripts | Define steps to reach state |

### Why Terraform?
- Cloud-agnostic (AWS, GCP, Azure, etc.)
- Declarative syntax (HCL)
- State management
- Plan before apply (safe changes)
- Module ecosystem
- Community-driven

---

## 2. Core Concepts

```
┌─────────────────────────────────────────┐
│          Terraform Workflow              │
│                                          │
│  Write → Plan → Apply → Destroy         │
│                                          │
│  1. Write: Define infrastructure in .tf  │
│  2. Plan: Preview changes                │
│  3. Apply: Create/modify infrastructure  │
│  4. Destroy: Tear everything down        │
└─────────────────────────────────────────┘
```

### HCL (HashiCorp Configuration Language)

```hcl
# main.tf

# Provider configuration
terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
  backend "s3" {
    bucket = "my-terraform-state"
    key    = "prod/terraform.tfstate"
    region = "us-east-1"
  }
}

provider "aws" {
  region = var.aws_region
}

# VPC
resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name        = "${var.project}-vpc"
    Environment = var.environment
  }
}

# Subnets
resource "aws_subnet" "public" {
  count             = length(var.availability_zones)
  vpc_id            = aws_vpc.main.id
  cidr_block        = cidrsubnet(aws_vpc.main.cidr_block, 8, count.index)
  availability_zone = var.availability_zones[count.index]

  map_public_ip_on_launch = true

  tags = {
    Name = "${var.project}-public-${count.index + 1}"
  }
}

# Security Group
resource "aws_security_group" "web" {
  name_prefix = "${var.project}-web-"
  vpc_id      = aws_vpc.main.id

  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# EC2 Instance
resource "aws_instance" "web" {
  ami           = data.aws_ami.ubuntu.id
  instance_type = var.instance_type
  subnet_id     = aws_subnet.public[0].id

  vpc_security_group_ids = [aws_security_group.web.id]
  key_name               = var.key_name

  user_data = <<-EOF
    #!/bin/bash
    apt-get update
    apt-get install -y docker.io
    docker run -d -p 80:3000 ${var.app_image}
  EOF

  tags = {
    Name = "${var.project}-web"
  }
}
```

---

## 3. Variables & Outputs

```hcl
# variables.tf
variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.medium"
}

variable "availability_zones" {
  type    = list(string)
  default = ["us-east-1a", "us-east-1b", "us-east-1c"]
}

variable "tags" {
  type = map(string)
  default = {
    Project   = "myapp"
    ManagedBy = "terraform"
  }
}

# outputs.tf
output "vpc_id" {
  description = "VPC ID"
  value       = aws_vpc.main.id
}

output "public_ip" {
  description = "Web server public IP"
  value       = aws_instance.web.public_ip
}

output "load_balancer_dns" {
  description = "ALB DNS name"
  value       = aws_lb.main.dns_name
}
```

---

## 4. Data Sources & State

```hcl
# Data sources (read existing resources)
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }
}

data "aws_caller_identity" "current" {}

# Remote state (read other project's state)
data "terraform_remote_state" "network" {
  backend = "s3"
  config = {
    bucket = "my-terraform-state"
    key    = "network/terraform.tfstate"
    region = "us-east-1"
  }
}

resource "aws_instance" "app" {
  subnet_id = data.terraform_remote_state.network.outputs.private_subnet_id
  # ...
}
```

---

## 5. Modules

```hcl
# modules/vpc/main.tf
resource "aws_vpc" "this" {
  cidr_block = var.cidr_block
  tags       = var.tags
}

# modules/vpc/variables.tf
variable "cidr_block" { type = string }
variable "tags" { type = map(string) }

# modules/vpc/outputs.tf
output "vpc_id" { value = aws_vpc.this.id }

# Usage in root module
module "vpc" {
  source     = "./modules/vpc"
  cidr_block = "10.0.0.0/16"
  tags       = { Name = "production-vpc" }
}

# Terraform Registry modules
module "vpc" {
  source  = "terraform-aws-modules/vpc/aws"
  version = "5.0.0"

  name = "my-vpc"
  cidr = "10.0.0.0/16"

  azs             = ["us-east-1a", "us-east-1b"]
  private_subnets = ["10.0.1.0/24", "10.0.2.0/24"]
  public_subnets  = ["10.0.101.0/24", "10.0.102.0/24"]

  enable_nat_gateway = true
}
```

---

## 6. Essential Commands

```bash
terraform init                    # Initialize, download providers
terraform plan                    # Preview changes
terraform apply                   # Apply changes
terraform apply -auto-approve     # Skip confirmation
terraform destroy                 # Destroy all resources
terraform fmt                     # Format code
terraform validate                # Validate syntax
terraform output                  # Show outputs
terraform state list              # List resources in state
terraform state show aws_instance.web  # Show specific resource
terraform import aws_instance.web i-123456  # Import existing resource
terraform taint aws_instance.web  # Mark for recreation
terraform workspace list          # List workspaces
terraform workspace new staging   # Create workspace
```

---

## 🎯 Interview Questions

### Q1: What is Terraform state and why is it important?
**A:** State maps real-world resources to your config. It tracks resource metadata, dependencies, and attributes. Stored in `terraform.tfstate`. Remote state (S3, GCS) enables team collaboration. State locking (DynamoDB) prevents concurrent modifications. Never manually edit state.

### Q2: How do you manage multiple environments in Terraform?
**A:** Three approaches: (1) **Workspaces**: `terraform workspace new staging` (simple but limited). (2) **Directory structure**: separate dirs per env with shared modules. (3) **Terragrunt**: DRY configuration wrapper. Most teams use directory structure + modules.

### Q3: What happens when you run `terraform plan`?
**A:** Terraform reads state file, queries real infrastructure, compares with desired config, and generates an execution plan showing: resources to create (+), modify (~), and destroy (-). No changes are made. Always review plan before apply.

### Q4: How do you handle secrets in Terraform?
**A:** Never put secrets in .tf files or state. Use: (1) Environment variables (`TF_VAR_`), (2) AWS Secrets Manager/Vault data sources, (3) Encrypted S3 backend for state, (4) `sensitive = true` on variables, (5) SOPS for encrypting tfvars files.

---

## 📝 Practice Exercises

1. Create a VPC with public/private subnets using Terraform
2. Deploy an EC2 instance with security groups and user data
3. Create reusable modules for VPC, EC2, and RDS
4. Set up remote state with S3 and DynamoDB locking
