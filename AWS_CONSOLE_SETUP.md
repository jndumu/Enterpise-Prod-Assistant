# 🔧 AWS Console Setup Guide
## Complete Step-by-Step Implementation

This guide provides detailed AWS Console configuration for Enterprise Production Assistant deployment.

---

## 📋 Prerequisites Checklist

Before starting, ensure you have:
- [ ] AWS Account with billing enabled
- [ ] Credit card attached to AWS account
- [ ] Admin email access for verification
- [ ] AstraDB account with database created
- [ ] Groq API key

---

## 🎯 STEP 1: AWS Account Setup

### 1.1 Create AWS Account (if needed)
1. **Go to**: https://aws.amazon.com
2. **Click**: "Create an AWS Account"
3. **Enter**: Email, password, AWS account name
4. **Select**: Personal account
5. **Complete**: Phone verification
6. **Add**: Credit/debit card (for billing)
7. **Choose**: Basic support plan (free)
8. **Verify**: Email and phone number

### 1.2 Sign in to AWS Console
1. **Go to**: https://console.aws.amazon.com
2. **Click**: "Sign in to the Console"
3. **Enter**: Root user email and password
4. **Complete**: MFA setup (recommended)

---

## 🔐 STEP 2: IAM User Creation (Critical)

### 2.1 Navigate to IAM Service
1. **AWS Console** → Search bar → Type "IAM"
2. **Click**: "IAM" from dropdown
3. **You should see**: IAM Dashboard

### 2.2 Create Deployment User
1. **Left sidebar** → Click "Users"
2. **Click**: "Create user" (orange button)
3. **Step 1 - User Details**:
   - User name: `enterprise-assistant-deploy`
   - Click "Next"

### 2.3 Set Permissions
1. **Step 2 - Permissions**:
   - Select "Attach policies directly"
   - **Search and check these policies** (use search box):
     - `AmazonECS_FullAccess`
     - `AmazonEC2ContainerRegistryFullAccess` 
     - `IAMFullAccess`
     - `AmazonVPCFullAccess`
     - `ElasticLoadBalancingFullAccess`
     - `AmazonSSMFullAccess`
     - `CloudWatchLogsFullAccess`
   - Click "Next"

### 2.4 Review and Create
1. **Step 3 - Review**:
   - Verify user name and 7 policies attached
   - Click "Create user"
2. **Success page** → Click "View user"

### 2.5 Create Access Keys
1. **On user page** → Click "Security credentials" tab
2. **Scroll down** → Click "Create access key"
3. **Step 1 - Access key best practices**:
   - Select "Application running outside AWS"
   - Check "I understand..." box
   - Click "Next"
4. **Step 2 - Description** (optional):
   - Description: `Enterprise Assistant Deployment`
   - Click "Create access key"
5. **Step 3 - Retrieve keys**:
   - **📝 COPY and SAVE**:
     - Access Key ID: `AKIA...`
     - Secret Access Key: `wJal...`
   - **⚠️ IMPORTANT**: Save these securely - you cannot see them again!
   - Click "Done"

---

## 🌍 STEP 3: Region Selection

### 3.1 Choose AWS Region
1. **Top right corner** → Click current region (e.g., "US East (N. Virginia)")
2. **Select**: "US East (N. Virginia) us-east-1" (recommended)
3. **Note**: This guide assumes us-east-1. Adjust commands if using different region.

---

## 🔍 STEP 4: Verify Services Are Available

### 4.1 Check ECS Service
1. **AWS Console** → Search "ECS"
2. **Click**: "Elastic Container Service"
3. **You should see**: ECS Dashboard with "Get Started" options

### 4.2 Check ECR Service  
1. **AWS Console** → Search "ECR"
2. **Click**: "Elastic Container Registry"
3. **You should see**: ECR Repositories page (empty initially)

### 4.3 Check VPC Service
1. **AWS Console** → Search "VPC"
2. **Click**: "VPC"  
3. **You should see**: VPC Dashboard with default VPC

---

## 💳 STEP 5: Billing and Cost Management

### 5.1 Set Up Billing Alerts
1. **AWS Console** → Search "Billing"
2. **Click**: "Billing and Cost Management"
3. **Left sidebar** → Click "Billing preferences"
4. **Enable**:
   - ✅ "Receive Free Tier Usage Alerts"
   - ✅ "Receive Billing Alerts"  
   - ✅ "Receive AWS Promotional Content"
5. **Enter**: Email address for alerts
6. **Click**: "Save preferences"

### 5.2 Create Cost Budget
1. **Left sidebar** → Click "Budgets"
2. **Click**: "Create budget"
3. **Select**: "Cost budget"
4. **Budget setup**:
   - Budget name: `Enterprise-Assistant-Monthly`
   - Period: Monthly
   - Budget amount: `$100` (adjust as needed)
5. **Alerting**:
   - Alert threshold: 80% of budget
   - Email: Your email address
6. **Click**: "Create budget"

---

## 🔒 STEP 6: Security Group Preparation

### 6.1 Navigate to EC2 Security Groups
1. **AWS Console** → Search "EC2"
2. **Click**: "EC2"
3. **Left sidebar** → Scroll down to "Network & Security"
4. **Click**: "Security Groups"
5. **Note**: You should see default security group (will create custom ones via Terraform)

---

## 📊 STEP 7: CloudWatch Setup

### 7.1 Access CloudWatch
1. **AWS Console** → Search "CloudWatch"
2. **Click**: "CloudWatch"
3. **Left sidebar** → Click "Log groups"
4. **You should see**: Empty log groups page (Terraform will create them)

---

## 🔧 STEP 8: Systems Manager (SSM) Verification

### 8.1 Check Parameter Store
1. **AWS Console** → Search "Systems Manager"
2. **Click**: "AWS Systems Manager"
3. **Left sidebar** → Under "Application Management" → Click "Parameter Store"
4. **You should see**: Empty parameter store (Terraform will populate)

---

## 🌐 STEP 9: Load Balancer Service Check

### 9.1 Verify ELB Service
1. **AWS Console** → Search "Load Balancing" or "ELB"
2. **Click**: "EC2" → Left sidebar → "Load Balancers"
3. **You should see**: Empty load balancer list (Terraform will create)

---

## ✅ STEP 10: Pre-Deployment Verification

### 10.1 Account Limits Check
1. **AWS Console** → Search "Service Quotas"
2. **Click**: "Service Quotas"
3. **Search for these services and verify default limits**:
   - **ECS**: Fargate tasks per service (default: 1000) ✅
   - **VPC**: VPCs per region (default: 5) ✅  
   - **ELB**: Application Load Balancers per region (default: 50) ✅
   - **ECR**: Repositories per region (default: 10,000) ✅

### 10.2 Final Checklist
- [ ] IAM user created with 7 policies attached
- [ ] Access keys generated and saved securely
- [ ] Region set to us-east-1 (or your preferred region)
- [ ] Billing alerts configured
- [ ] Cost budget created
- [ ] All required services accessible
- [ ] Account limits verified

---

## 🚀 STEP 11: Ready for Terraform Deployment

### 11.1 Your AWS Console is now ready!
With these steps completed, you can now:

1. **Run Terraform deployment**:
   ```bash
   cd infrastructure
   terraform init
   terraform apply
   ```

2. **Monitor progress in AWS Console**:
   - **ECS** → Clusters (new cluster will appear)
   - **ECR** → Repositories (new repository will appear)
   - **VPC** → Your VPCs (new VPC will appear)
   - **EC2** → Load Balancers (new ALB will appear)
   - **CloudWatch** → Log groups (new log groups will appear)

---

## 🔍 STEP 12: Post-Deployment Verification

### 12.1 Check Created Resources
After Terraform deployment, verify in AWS Console:

1. **ECS Console**:
   - Cluster: `enterprise-assistant` should exist
   - Service: `enterprise-assistant-service` should be running
   - Tasks: Should show 1/1 running

2. **ECR Console**:
   - Repository: `enterprise-assistant` should exist
   - Should show image after first deployment

3. **VPC Console**:
   - New VPC: `enterprise-assistant-vpc` should exist
   - Subnets: 2 public subnets should exist

4. **Load Balancer Console**:
   - ALB: `enterprise-assistant` should exist
   - State: Should be "Active"
   - Target group: Should show healthy targets

5. **CloudWatch Console**:
   - Log group: `/ecs/enterprise-assistant` should exist
   - Should show log streams after deployment

---

## 🔧 Troubleshooting Common Issues

### Issue 1: "Access Denied" errors
**Solution**: Verify IAM user has all 7 policies attached

### Issue 2: "Service not available in region"  
**Solution**: Switch to us-east-1 region or update Terraform variables

### Issue 3: "Billing not enabled"
**Solution**: Add payment method in Billing console

### Issue 4: "Resource limit exceeded"
**Solution**: Check Service Quotas and request increase if needed

---

## 📱 Monitoring Your Deployment

### Real-time Monitoring Locations:
1. **ECS Console** → enterprise-assistant cluster
2. **CloudWatch** → Log groups → /ecs/enterprise-assistant  
3. **EC2** → Load Balancers → enterprise-assistant
4. **Systems Manager** → Parameter Store (for secrets)

---

## 💰 Cost Monitoring

### Expected Monthly Costs:
- **Application Load Balancer**: ~$16/month
- **ECS Fargate**: ~$35/month (1 task)
- **ECR Storage**: ~$1/month
- **CloudWatch Logs**: ~$3/month
- **Data Transfer**: ~$5/month
- **Total**: ~$60/month

### Cost Alerts:
- Check Billing Dashboard weekly
- Review Cost Explorer for trends
- Monitor budget alerts via email

---

## 🎉 Success!

Your AWS Console is now fully configured for Enterprise Production Assistant deployment!

**Next Steps**:
1. Save your IAM access keys securely
2. Run Terraform deployment
3. Monitor resource creation in AWS Console
4. Test application via Load Balancer URL

**🌟 You're ready to deploy your production application!**