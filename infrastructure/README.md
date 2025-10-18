# Infrastructure

AWS infrastructure as code using Terraform.

## 📁 Structure

```
infrastructure/
├── main.tf                 # Core AWS resources (VPC, ECS, ALB)
├── iam.tf                  # IAM roles and policies
├── ssm.tf                  # Secure parameter store for API keys
├── variables.tf            # Input variables
├── outputs.tf              # Resource outputs
├── terraform.tfvars.example # Configuration template
└── docker/                 # Container configuration
```

## 🚀 Quick Deploy

```bash
# 1. Configure variables
cp terraform.tfvars.example terraform.tfvars
# Edit terraform.tfvars with your API keys

# 2. Deploy infrastructure
terraform init
terraform plan
terraform apply

# 3. Get application URL
terraform output application_url
```

## 📋 Resources Created

- **VPC** with public subnets across 2 AZs
- **Application Load Balancer** for public access
- **ECS Fargate** cluster and service
- **ECR** repository for container images
- **CloudWatch** log groups
- **SSM Parameter Store** for secure API key storage
- **IAM roles** with least-privilege access

## 💰 Estimated Cost

~$55/month for production workload

## 🧹 Cleanup

```bash
terraform destroy
```