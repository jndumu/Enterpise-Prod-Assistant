#!/bin/bash
# Minimal deployment script - one command deploy

echo "🚀 Deploying Minimal Enterprise Assistant..."

# Build with minimal requirements
docker build -f Dockerfile.minimal -t enterprise-assistant-minimal .

# Tag for ECR
docker tag enterprise-assistant-minimal:latest 135334155695.dkr.ecr.us-east-2.amazonaws.com/enterprise-assistant:latest

# Push to ECR (requires: aws ecr get-login-password --region us-east-2 | docker login ...)
docker push 135334155695.dkr.ecr.us-east-2.amazonaws.com/enterprise-assistant:latest

# Update ECS service
aws ecs update-service --cluster enterprise-assistant --service enterprise-assistant-simple-service --force-new-deployment --region us-east-2

echo "✅ Deployment initiated! Check http://3.19.65.199:8000 in 2-3 minutes"