# Day 18: Infrastructure as Code

## Status: ⬜ Not Started

---

## 📚 Learning Goals

### 1. Terraform
- [ ] Understand Terraform concepts
- [ ] Know HCL syntax

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Infrastructure as Code Flow                                             │
│                                                                         │
│   Developer                                                             │
│  ┌──────────────┐                                                       │
│  │  Write HCL   │                                                       │
│  │  (Terraform) │                                                       │
│  └──────┬───────┘                                                       │
│         │                                                               │
│         ▼                                                               │
│  ┌──────────────┐     ┌──────────────┐     ┌──────────────┐           │
│  │   terraform  │────►│   terraform  │────►│   terraform  │           │
│  │     init     │     │     plan     │     │    apply     │           │
│  └──────────────┘     └──────────────┘     └──────────────┘           │
│                              │                     │                    │
│                              ▼                     ▼                    │
│                       ┌─────────────┐       ┌─────────────┐            │
│                       │  Review     │       │  Provision  │            │
│                       │  Changes    │       │  Resources  │            │
│                       └─────────────┘       └─────────────┘            │
│                                                    │                    │
│                                                    ▼                    │
│                              ┌──────────────────────────────────────┐  │
│                              │          Cloud Provider              │  │
│                              │  ┌──────┐ ┌──────┐ ┌──────┐         │  │
│                              │  │ VPC  │ │ EC2  │ │ RDS  │         │  │
│                              │  └──────┘ └──────┘ └──────┘         │  │
│                              └──────────────────────────────────────┘  │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Terraform Example:**

```hcl
# provider.tf
terraform {
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
  region = var.region
}

# variables.tf
variable "region" {
  default = "us-east-1"
}

variable "environment" {
  default = "production"
}

# main.tf
module "vpc" {
  source = "./modules/vpc"
  
  cidr_block  = "10.0.0.0/16"
  environment = var.environment
}

module "eks" {
  source = "./modules/eks"
  
  vpc_id     = module.vpc.vpc_id
  subnet_ids = module.vpc.private_subnet_ids
}

# outputs.tf
output "cluster_endpoint" {
  value = module.eks.cluster_endpoint
}
```

**Terraform State Management:**

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Remote State Management                                                 │
│                                                                         │
│   Team A             Team B             Team C                          │
│  ┌──────────┐       ┌──────────┐       ┌──────────┐                    │
│  │terraform │       │terraform │       │terraform │                    │
│  │ apply    │       │ apply    │       │ apply    │                    │
│  └────┬─────┘       └────┬─────┘       └────┬─────┘                    │
│       │                  │                  │                          │
│       └──────────────────┼──────────────────┘                          │
│                          │                                              │
│                          ▼                                              │
│              ┌───────────────────────┐                                 │
│              │   Remote State Store  │                                 │
│              │   (S3 + DynamoDB)     │                                 │
│              │                       │                                 │
│              │   State Locking ✓     │                                 │
│              │   Version Control ✓   │                                 │
│              │   Encryption ✓        │                                 │
│              └───────────────────────┘                                 │
│                                                                         │
│  Benefits:                                                             │
│  • Team collaboration                                                  │
│  • State locking prevents conflicts                                    │
│  • Version history                                                     │
│  • Secure storage                                                      │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

### 2. ARM Templates / CloudFormation
- [ ] Understand declarative templates
- [ ] Know cloud-specific IaC

**CloudFormation Example:**

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Description: 'VPC with public and private subnets'

Parameters:
  EnvironmentName:
    Type: String
    Default: production

Resources:
  VPC:
    Type: AWS::EC2::VPC
    Properties:
      CidrBlock: 10.0.0.0/16
      EnableDnsHostnames: true
      Tags:
        - Key: Name
          Value: !Sub ${EnvironmentName}-vpc

  PublicSubnet:
    Type: AWS::EC2::Subnet
    Properties:
      VpcId: !Ref VPC
      CidrBlock: 10.0.1.0/24
      AvailabilityZone: !Select [0, !GetAZs '']
      MapPublicIpOnLaunch: true

  InternetGateway:
    Type: AWS::EC2::InternetGateway

  AttachGateway:
    Type: AWS::EC2::VPCGatewayAttachment
    Properties:
      VpcId: !Ref VPC
      InternetGatewayId: !Ref InternetGateway

Outputs:
  VpcId:
    Value: !Ref VPC
    Export:
      Name: !Sub ${EnvironmentName}-VpcId
```

---

### 3. Immutable Infrastructure
- [ ] Understand immutable vs mutable
- [ ] Know golden image pattern

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Mutable vs Immutable Infrastructure                                     │
│                                                                         │
│  Mutable (Traditional):                                                │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                                                                 │   │
│  │  Server v1.0 ──► Patch ──► Update ──► Patch ──► v1.3          │   │
│  │                                                                 │   │
│  │  • Configuration drift                                         │   │
│  │  • "Snowflake" servers                                         │   │
│  │  • Hard to reproduce                                           │   │
│  │                                                                 │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
│  Immutable (Modern):                                                   │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                                                                 │   │
│  │  AMI v1.0 ──► Deploy ──► (need update?) ──► AMI v1.1 ──► Deploy│   │
│  │                              │                                  │   │
│  │                              └──►  Terminate old servers       │   │
│  │                                                                 │   │
│  │  • Consistent environments                                     │   │
│  │  • Easy rollback                                               │   │
│  │  • Reproducible                                                │   │
│  │                                                                 │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Golden Image Pipeline:**

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Golden Image Pipeline (Packer)                                          │
│                                                                         │
│   ┌───────────┐     ┌───────────┐     ┌───────────┐     ┌───────────┐ │
│   │  Base OS  │────►│  Install  │────►│  Harden   │────►│  AMI      │ │
│   │  Image    │     │  Software │     │  Security │     │  Output   │ │
│   └───────────┘     └───────────┘     └───────────┘     └───────────┘ │
│                                                                         │
│  Packer Template:                                                      │
│  {                                                                     │
│    "builders": [{                                                      │
│      "type": "amazon-ebs",                                            │
│      "source_ami": "ami-12345",                                       │
│      "instance_type": "t3.micro"                                      │
│    }],                                                                │
│    "provisioners": [{                                                 │
│      "type": "shell",                                                 │
│      "script": "setup.sh"                                            │
│    }]                                                                 │
│  }                                                                     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 📘 IaC Best Practices

### Module Structure

```
terraform/
├── environments/
│   ├── dev/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── terraform.tfvars
│   ├── staging/
│   └── production/
├── modules/
│   ├── vpc/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── eks/
│   └── rds/
└── global/
    └── iam/
```

### Terraform Best Practices

```hcl
# Use data sources to reference existing resources
data "aws_ami" "ubuntu" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }
}

# Use locals for computed values
locals {
  common_tags = {
    Environment = var.environment
    ManagedBy   = "terraform"
    Project     = var.project_name
  }
}

# Use count or for_each for multiple resources
resource "aws_instance" "app" {
  count         = var.instance_count
  ami           = data.aws_ami.ubuntu.id
  instance_type = var.instance_type
  
  tags = merge(local.common_tags, {
    Name = "app-${count.index + 1}"
  })
}

# Validate inputs
variable "environment" {
  type = string
  validation {
    condition     = contains(["dev", "staging", "production"], var.environment)
    error_message = "Environment must be dev, staging, or production."
  }
}
```

---

## 🎯 Practice Task

### Build Cloud Infrastructure

**Instructions:**
1. Create Terraform modules for VPC, EKS, RDS
2. Use remote state in S3
3. Implement different environments (dev, prod)
4. Document the architecture

---

## 📝 Notes

*Add your notes here during learning*

---

## 📖 Resources

- [ ] [Terraform Documentation](https://www.terraform.io/docs)
- [ ] [AWS CloudFormation](https://docs.aws.amazon.com/cloudformation/)
- [ ] [Packer Documentation](https://www.packer.io/docs)

---

## ✅ Completion Checklist

- [ ] Understand Terraform workflow
- [ ] Can write Terraform modules
- [ ] Know state management
- [ ] Understand immutable infrastructure
- [ ] Completed practice task

**Date Completed:** _____________
