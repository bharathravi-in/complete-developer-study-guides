# Day 15: Cloud Architecture

## Status: ⬜ Not Started

---

## 📚 Learning Goals

### 1. Cloud Service Models
- [ ] Understand IaaS, PaaS, SaaS
- [ ] Know responsibilities at each level

```
┌─────────────────────────────────────────────────────────────────────────┐
│  Cloud Service Models                                                    │
│                                                                         │
│   On-Premises     IaaS          PaaS          SaaS                     │
│                                                                         │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌───────────┐           │
│  │Application│  │Application│  │Application│  │███████████│           │
│  ├───────────┤  ├───────────┤  ├───────────┤  ├───────────┤           │
│  │   Data    │  │   Data    │  │   Data    │  │███████████│           │
│  ├───────────┤  ├───────────┤  ├───────────┤  ├───────────┤           │
│  │  Runtime  │  │  Runtime  │  │███████████│  │███████████│           │
│  ├───────────┤  ├───────────┤  ├───████████│  ├███████████┤           │
│  │Middleware │  │Middleware │  │███████████│  │███████████│           │
│  ├───────────┤  ├───────────┤  ├███████████┤  ├███████████┤           │
│  │    O/S    │  │    O/S    │  │███████████│  │███████████│           │
│  ├───────────┤  ├───────────┤  ├███████████┤  ├███████████┤           │
│  │Virtualize │  │███████████│  │███████████│  │███████████│           │
│  ├───────────┤  ├███████████┤  ├███████████┤  ├███████████┤           │
│  │  Servers  │  │███████████│  │███████████│  │███████████│           │
│  ├───────────┤  ├███████████┤  ├███████████┤  ├███████████┤           │
│  │  Storage  │  │███████████│  │███████████│  │███████████│           │
│  ├───────────┤  ├███████████┤  ├███████████┤  ├███████████┤           │
│  │ Networking│  │███████████│  │███████████│  │███████████│           │
│  └───────────┘  └───────────┘  └───────────┘  └───────────┘           │
│                                                                         │
│  ▓▓▓ = Managed by Cloud Provider                                       │
│                                                                         │
│  You Manage    You Manage    You Manage    You Manage                  │
│  Everything    App, Data,    App, Data     Nothing                     │
│                OS, Runtime                 (Just use it)               │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Examples:**

| Model | Examples | Use Case |
|-------|----------|----------|
| **IaaS** | EC2, Azure VMs, GCE | Full control, custom environments |
| **PaaS** | Heroku, App Engine, Elastic Beanstalk | Focus on code, not infra |
| **SaaS** | Salesforce, Office 365, Gmail | Ready-to-use applications |
| **FaaS** | Lambda, Azure Functions | Event-driven, serverless |

---

### 2. Multi-Cloud vs Hybrid Cloud
- [ ] Understand deployment models
- [ ] Know trade-offs

```
Multi-Cloud Architecture:
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    │
│  │      AWS        │    │     Azure       │    │      GCP        │    │
│  │                 │    │                 │    │                 │    │
│  │  Compute (EC2)  │    │  AI/ML Services │    │  BigQuery       │    │
│  │  S3 Storage     │    │  Active Dir     │    │  Kubernetes     │    │
│  │  RDS Database   │    │  Office 365     │    │  Analytics      │    │
│  │                 │    │                 │    │                 │    │
│  └────────┬────────┘    └────────┬────────┘    └────────┬────────┘    │
│           │                      │                      │              │
│           └──────────────────────┼──────────────────────┘              │
│                                  │                                      │
│                        ┌─────────▼─────────┐                           │
│                        │  Multi-Cloud      │                           │
│                        │  Management       │                           │
│                        │  (Terraform)      │                           │
│                        └───────────────────┘                           │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘

Hybrid Cloud Architecture:
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│  ┌─────────────────────────┐         ┌─────────────────────────┐       │
│  │   On-Premises           │         │     Public Cloud        │       │
│  │   Data Center           │         │       (AWS)             │       │
│  │                         │   VPN   │                         │       │
│  │  ┌───────┐ ┌───────┐   │◄───────►│  ┌───────┐ ┌───────┐   │       │
│  │  │Legacy │ │Sensitiv│   │ /Direct │  │  Web  │ │ Burst │   │       │
│  │  │Systems│ │ Data  │   │ Connect │  │  Apps │ │Compute│   │       │
│  │  └───────┘ └───────┘   │         │  └───────┘ └───────┘   │       │
│  │                         │         │                         │       │
│  └─────────────────────────┘         └─────────────────────────┘       │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

| Approach | Pros | Cons |
|----------|------|------|
| **Multi-Cloud** | Avoid lock-in, best-of-breed | Complexity, cost |
| **Hybrid** | Data sovereignty, gradual migration | Integration challenges |

---

### 3. AWS Core Services
- [ ] Learn essential AWS services
- [ ] Know when to use each

```
┌─────────────────────────────────────────────────────────────────────────┐
│  AWS Core Services for Architects                                        │
│                                                                         │
│  COMPUTE                    STORAGE                 DATABASE            │
│  ┌─────────────┐           ┌─────────────┐         ┌─────────────┐     │
│  │ EC2         │           │ S3          │         │ RDS         │     │
│  │ Lambda      │           │ EBS         │         │ DynamoDB    │     │
│  │ ECS/EKS     │           │ EFS         │         │ ElastiCache │     │
│  │ Fargate     │           │ Glacier     │         │ Aurora      │     │
│  └─────────────┘           └─────────────┘         └─────────────┘     │
│                                                                         │
│  NETWORKING                 SECURITY                INTEGRATION         │
│  ┌─────────────┐           ┌─────────────┐         ┌─────────────┐     │
│  │ VPC         │           │ IAM         │         │ SQS         │     │
│  │ Route 53    │           │ KMS         │         │ SNS         │     │
│  │ CloudFront  │           │ WAF         │         │ API Gateway │     │
│  │ ALB/NLB     │           │ Secrets Mgr │         │ EventBridge │     │
│  └─────────────┘           └─────────────┘         └─────────────┘     │
│                                                                         │
│  MONITORING                 ML/AI                  DEVELOPER TOOLS      │
│  ┌─────────────┐           ┌─────────────┐         ┌─────────────┐     │
│  │ CloudWatch  │           │ SageMaker   │         │ CodePipeline│     │
│  │ X-Ray       │           │ Bedrock     │         │ CodeBuild   │     │
│  │ CloudTrail  │           │ Rekognition │         │ CodeDeploy  │     │
│  └─────────────┘           └─────────────┘         └─────────────┘     │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

**Key Service Categories:**

| Category | Service | Purpose |
|----------|---------|---------|
| **Compute** | EC2, Lambda, ECS | Run workloads |
| **Storage** | S3, EBS, EFS | Store data |
| **Database** | RDS, DynamoDB | Managed databases |
| **Networking** | VPC, ALB, CloudFront | Connectivity, delivery |
| **Security** | IAM, KMS, WAF | Access control, encryption |

---

### 4. Azure Basics
- [ ] Understand Azure equivalents

```
AWS to Azure Mapping:
┌─────────────────┬─────────────────┬───────────────────────────────────┐
│      AWS        │     Azure       │          Purpose                  │
├─────────────────┼─────────────────┼───────────────────────────────────┤
│ EC2             │ Virtual Machines│ Compute instances                 │
│ Lambda          │ Azure Functions │ Serverless compute                │
│ S3              │ Blob Storage    │ Object storage                    │
│ RDS             │ Azure SQL DB    │ Managed relational DB             │
│ DynamoDB        │ Cosmos DB       │ NoSQL database                    │
│ VPC             │ Virtual Network │ Network isolation                 │
│ CloudFront      │ Azure CDN       │ Content delivery                  │
│ IAM             │ Azure AD / RBAC │ Identity management               │
│ CloudWatch      │ Azure Monitor   │ Monitoring                        │
│ SQS             │ Service Bus     │ Message queuing                   │
│ EKS             │ AKS             │ Managed Kubernetes                │
└─────────────────┴─────────────────┴───────────────────────────────────┘
```

---

### 5. GCP Basics
- [ ] Understand GCP services

```
AWS to GCP Mapping:
┌─────────────────┬─────────────────┬───────────────────────────────────┐
│      AWS        │      GCP        │          Purpose                  │
├─────────────────┼─────────────────┼───────────────────────────────────┤
│ EC2             │ Compute Engine  │ Virtual machines                  │
│ Lambda          │ Cloud Functions │ Serverless                        │
│ S3              │ Cloud Storage   │ Object storage                    │
│ RDS             │ Cloud SQL       │ Managed relational DB             │
│ DynamoDB        │ Firestore       │ NoSQL database                    │
│ VPC             │ VPC             │ Network                           │
│ CloudFront      │ Cloud CDN       │ CDN                               │
│ IAM             │ Cloud IAM       │ Identity                          │
│ CloudWatch      │ Cloud Monitoring│ Monitoring                        │
│ EKS             │ GKE             │ Kubernetes                        │
│ Redshift        │ BigQuery        │ Data warehouse                    │
└─────────────────┴─────────────────┴───────────────────────────────────┘
```

**GCP Strengths:**
- BigQuery (data analytics)
- GKE (Kubernetes)
- AI/ML services
- Global network

---

## 📘 Well-Architected Framework

### AWS Well-Architected 6 Pillars

```
┌─────────────────────────────────────────────────────────────────────────┐
│                                                                         │
│     ┌─────────────────────────────────────────────────────────────┐    │
│     │              Well-Architected Framework                      │    │
│     │                                                             │    │
│     │  1. Operational Excellence                                   │    │
│     │     - Automate changes                                       │    │
│     │     - Respond to events                                      │    │
│     │     - Define standards                                       │    │
│     │                                                             │    │
│     │  2. Security                                                 │    │
│     │     - Protect data and systems                              │    │
│     │     - IAM, encryption, compliance                           │    │
│     │                                                             │    │
│     │  3. Reliability                                              │    │
│     │     - Recover from failures                                  │    │
│     │     - Meet demand                                            │    │
│     │                                                             │    │
│     │  4. Performance Efficiency                                   │    │
│     │     - Use resources efficiently                             │    │
│     │     - Select right resources                                │    │
│     │                                                             │    │
│     │  5. Cost Optimization                                        │    │
│     │     - Avoid unnecessary costs                               │    │
│     │     - Right-sizing                                          │    │
│     │                                                             │    │
│     │  6. Sustainability                                           │    │
│     │     - Minimize environmental impact                         │    │
│     │     - Efficient resource use                                │    │
│     │                                                             │    │
│     └─────────────────────────────────────────────────────────────┘    │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Practice Task

### Design Cloud Architecture

**Instructions:**
1. Design a cloud architecture for a SaaS application
2. Choose appropriate services from AWS/Azure/GCP
3. Consider: Multi-region, High availability
4. Cost optimization

---

## 📝 Notes

*Add your notes here during learning*

---

## 📖 Resources

- [ ] [AWS Well-Architected](https://aws.amazon.com/architecture/)
- [ ] [Azure Architecture Center](https://docs.microsoft.com/en-us/azure/architecture/)
- [ ] [GCP Architecture Framework](https://cloud.google.com/architecture/framework)

---

## ✅ Completion Checklist

- [ ] Understood IaaS, PaaS, SaaS
- [ ] Know multi-cloud vs hybrid
- [ ] Familiar with AWS core services
- [ ] Know Azure basics
- [ ] Know GCP basics
- [ ] Understand Well-Architected Framework

**Date Completed:** _____________
