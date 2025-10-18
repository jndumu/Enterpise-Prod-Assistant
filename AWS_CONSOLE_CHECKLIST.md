# ✅ AWS Console Setup Checklist

Quick verification checklist for AWS Console setup.

## 🔥 Critical Steps (Must Complete)

### IAM User Setup
- [ ] Created IAM user: `enterprise-assistant-deploy`
- [ ] Attached 7 required policies:
  - [ ] AmazonECS_FullAccess
  - [ ] AmazonEC2ContainerRegistryFullAccess
  - [ ] IAMFullAccess
  - [ ] AmazonVPCFullAccess  
  - [ ] ElasticLoadBalancingFullAccess
  - [ ] AmazonSSMFullAccess
  - [ ] CloudWatchLogsFullAccess
- [ ] Generated Access Key ID and Secret Key
- [ ] Saved keys securely (cannot retrieve again!)

### Basic Configuration
- [ ] AWS account has billing enabled
- [ ] Credit card attached to account
- [ ] Region set to `us-east-1` (or consistent region)
- [ ] All required services accessible:
  - [ ] ECS (Elastic Container Service)
  - [ ] ECR (Elastic Container Registry)
  - [ ] VPC (Virtual Private Cloud)
  - [ ] CloudWatch (Logging)
  - [ ] Systems Manager (Parameter Store)

## 💰 Cost Management
- [ ] Billing alerts enabled
- [ ] Cost budget created ($100 recommended)
- [ ] Email notifications configured

## 🚀 Ready to Deploy
- [ ] All checkboxes above completed
- [ ] Access keys saved in secure location
- [ ] Region consistently set across all services

**🎯 Time to deploy: `cd infrastructure && terraform apply`**