# 🚀 AWS Deployment Guide
## Enterprise Production Assistant

Complete step-by-step guide for deploying to AWS with public access.

## 📋 Prerequisites

### Required Accounts & API Keys:
1. **AWS Account** with billing enabled
2. **AstraDB Account** with database setup
3. **Groq API Key** 
4. **GitHub Repository** (already done ✅)

### Required Tools:
- AWS CLI v2
- Terraform >= 1.0
- Docker (for local testing)

---

## 🔧 Step 1: AWS Console Setup

### 1.1 Create IAM User for Deployment
1. **Login to AWS Console** → IAM → Users
2. **Create User**: `enterprise-assistant-deploy`
3. **Attach Policies**:
   - `AmazonECS_FullAccess`
   - `AmazonEC2ContainerRegistryFullAccess`
   - `IAMFullAccess`
   - `AmazonVPCFullAccess`
   - `ElasticLoadBalancingFullAccess`
   - `AmazonSSMFullAccess`
   - `CloudWatchLogsFullAccess`
4. **Create Access Keys** → Save `Access Key ID` & `Secret Access Key`

### 1.2 Configure AWS CLI
```bash
aws configure
# Enter your Access Key ID
# Enter your Secret Access Key  
# Default region: us-east-1
# Default output: json
```

### 1.3 Verify AWS Setup
```bash
aws sts get-caller-identity
# Should show your account ID and user ARN
```

---

## 🏗️ Step 2: Infrastructure Deployment

### 2.1 Prepare Terraform Variables
```bash
cd infra
cp terraform.tfvars.example terraform.tfvars
```

### 2.2 Edit `terraform.tfvars` with your values:
```hcl
app_name    = "enterprise-assistant"
aws_region  = "us-east-1"

# Get these from your accounts
astra_db_token    = "AstraCS:your_actual_token_here"
astra_db_endpoint = "https://your-actual-endpoint.apps.astra.datastax.com"
groq_api_key      = "gsk_your_actual_groq_key_here"
serper_api_key    = "your_serper_key_here"  # Optional
```

### 2.3 Deploy Infrastructure
```bash
# Initialize Terraform
terraform init

# Review what will be created
terraform plan

# Deploy (takes ~5-10 minutes)
terraform apply
# Type 'yes' when prompted

# Save the outputs - you'll need the application_url
terraform output
```

**Expected Outputs:**
```
application_url = "http://enterprise-assistant-123456789.us-east-1.elb.amazonaws.com"
ecr_repository_url = "123456789.dkr.ecr.us-east-1.amazonaws.com/enterprise-assistant"
```

---

## 🐳 Step 3: Build & Deploy Application

### 3.1 Build and Push Docker Image
```bash
# Go back to project root
cd ..

# Get ECR login command
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin $(aws sts get-caller-identity --query Account --output text).dkr.ecr.us-east-1.amazonaws.com

# Build image
docker build -t enterprise-assistant .

# Tag for ECR (replace ACCOUNT_ID with your actual account ID)
docker tag enterprise-assistant:latest $(aws sts get-caller-identity --query Account --output text).dkr.ecr.us-east-1.amazonaws.com/enterprise-assistant:latest

# Push to ECR
docker push $(aws sts get-caller-identity --query Account --output text).dkr.ecr.us-east-1.amazonaws.com/enterprise-assistant:latest
```

### 3.2 Deploy to ECS
```bash
# Update ECS service to use new image
aws ecs update-service \
  --cluster enterprise-assistant \
  --service enterprise-assistant-service \
  --force-new-deployment \
  --region us-east-1

# Wait for deployment to complete
aws ecs wait services-stable \
  --cluster enterprise-assistant \
  --services enterprise-assistant-service \
  --region us-east-1
```

---

## 🔍 Step 4: Verify Deployment

### 4.1 Check ECS Service Status
```bash
aws ecs describe-services \
  --cluster enterprise-assistant \
  --services enterprise-assistant-service \
  --query 'services[0].{Status:status,RunningCount:runningCount,DesiredCount:desiredCount}' \
  --output table
```

### 4.2 Check Application Health
```bash
# Get your application URL from Terraform output
LOAD_BALANCER_URL=$(terraform -chdir=infra output -raw application_url)
echo "Application URL: $LOAD_BALANCER_URL"

# Test health endpoint
curl "$LOAD_BALANCER_URL/health"
# Should return: {"status": "healthy", "components": {...}}
```

### 4.3 Test Application
```bash
# Test query endpoint
curl -X POST "$LOAD_BALANCER_URL/query" \
  -H "Content-Type: application/json" \
  -d '{"question": "What is machine learning?"}'
```

---

## 🌐 Step 5: GitHub Actions Setup

### 5.1 Add GitHub Secrets
Go to your GitHub repository → Settings → Secrets and variables → Actions

**Add these Repository Secrets:**
```
AWS_ACCESS_KEY_ID = your_access_key_id_from_step_1.1
AWS_SECRET_ACCESS_KEY = your_secret_key_from_step_1.1
AWS_ACCOUNT_ID = your_12_digit_account_id
ASTRA_DB_APPLICATION_TOKEN = your_astra_token
ASTRA_DB_API_ENDPOINT = your_astra_endpoint  
GROQ_API_KEY = your_groq_key
SERPER_API_KEY = your_serper_key (optional)
```

### 5.2 Test GitHub Actions
1. **Push any change** to main branch
2. **Check Actions tab** in GitHub
3. **Verify deployment** completes successfully

---

## 📊 Step 6: Monitoring & Logs

### 6.1 View Application Logs
```bash
# View logs in CloudWatch
aws logs describe-log-groups --log-group-name-prefix "/ecs/enterprise-assistant"

# Get recent logs
aws logs get-log-events \
  --log-group-name "/ecs/enterprise-assistant" \
  --log-stream-name "$(aws logs describe-log-streams --log-group-name "/ecs/enterprise-assistant" --query 'logStreams[0].logStreamName' --output text)" \
  --start-time $(date -d '5 minutes ago' +%s)000
```

### 6.2 Monitor in AWS Console
- **ECS Console** → Clusters → enterprise-assistant
- **CloudWatch** → Log groups → /ecs/enterprise-assistant  
- **EC2** → Load Balancers → enterprise-assistant

---

## 🔧 Step 7: Common Issues & Troubleshooting

### Issue: Service Won't Start
```bash
# Check service events
aws ecs describe-services \
  --cluster enterprise-assistant \
  --services enterprise-assistant-service \
  --query 'services[0].events[0:5]'
```

### Issue: Health Check Fails
```bash
# Check task logs
aws logs get-log-events \
  --log-group-name "/ecs/enterprise-assistant" \
  --log-stream-name "$(aws logs describe-log-streams --log-group-name "/ecs/enterprise-assistant" --query 'logStreams[0].logStreamName' --output text)"
```

### Issue: Can't Access Application
1. **Check Security Group**: Port 80 should be open to 0.0.0.0/0
2. **Check Target Group Health**: Should show healthy targets
3. **Check DNS Propagation**: May take 1-2 minutes

---

## 🎯 Step 8: Final Verification

### 8.1 Public Access Test
1. **Get your application URL** from Terraform output
2. **Open in browser**: `http://your-load-balancer-url.elb.amazonaws.com`
3. **Test endpoints**:
   - Health: `/health`
   - Query: `/query` (POST with JSON body)

### 8.2 Performance Check
```bash
# Test response time
time curl "$LOAD_BALANCER_URL/health"

# Test concurrent requests
for i in {1..5}; do
  curl "$LOAD_BALANCER_URL/health" &
done
wait
```

---

## 🎉 Success Criteria

✅ **Infrastructure deployed** via Terraform  
✅ **Application container running** in ECS  
✅ **Load balancer healthy** and publicly accessible  
✅ **Health endpoint** returns 200 OK  
✅ **Query endpoint** processes questions  
✅ **GitHub Actions** deploys automatically  
✅ **Logs visible** in CloudWatch  

**🌟 Your Enterprise Production Assistant is now live and accessible to users worldwide!**

---

## 💰 Cost Estimate

**Monthly AWS costs (approximate):**
- ALB: ~$16/month
- ECS Fargate: ~$35/month (1 task)
- ECR: ~$1/month
- CloudWatch: ~$3/month
- **Total: ~$55/month**

## 🧹 Cleanup (when needed)

```bash
# Destroy infrastructure
cd infra
terraform destroy
# Type 'yes' when prompted

# This will remove all AWS resources and stop charges
```