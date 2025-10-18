# Production RAG Application - AWS Deployment Guide

## 🚀 Pre-Deployment Checklist

### Environment Variables
Add these to GitHub Secrets:
```
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
ASTRA_DB_APPLICATION_TOKEN=your_token
ASTRA_DB_API_ENDPOINT=your_endpoint
GROQ_API_KEY=your_groq_key
SERPER_API_KEY=your_serper_key (optional)
```

### Prerequisites
- AWS Account with ECS/ECR permissions
- GitHub repository
- Domain name (optional)

## 🏗️ Infrastructure Setup

1. **Deploy AWS Infrastructure**:
```bash
cd infrastructure
terraform init
terraform plan
terraform apply
```

2. **Configure DNS** (optional):
   - Point your domain to the ALB DNS name
   - Add SSL certificate in AWS Certificate Manager

## 🔧 Application Features

### Enhanced Web Search
- **Serper API**: Real-time Google search results
- **Wikipedia API**: Factual information
- **DuckDuckGo**: Fallback search
- **Groq Integration**: AI-powered summarization

### Content Moderation
- **Profanity Filter**: Blocks inappropriate language
- **Harmful Content**: Prevents dangerous requests  
- **Safety Guardrails**: Educational use enforcement

### Production Architecture
- **Multi-stage Docker**: Optimized container size
- **ECS Fargate**: Serverless container hosting
- **Auto Scaling**: Handles traffic spikes
- **Health Checks**: Ensures reliability
- **Load Balancer**: High availability

## 🚢 Deployment Process

### Automatic Deployment
1. Push to `main` branch
2. GitHub Actions runs tests
3. Builds Docker image
4. Pushes to ECR
5. Deploys to ECS
6. Updates load balancer

### Manual Deployment
```bash
# Build locally
docker build -t rag-app .

# Tag for ECR
docker tag rag-app:latest YOUR_ECR_URI:latest

# Push to ECR
docker push YOUR_ECR_URI:latest

# Update ECS service
aws ecs update-service --cluster rag-app-cluster --service rag-app-service --force-new-deployment
```

## 📊 Monitoring & Scaling

### CloudWatch Metrics
- CPU/Memory utilization
- Request count and latency
- Error rates
- Health check status

### Auto Scaling
- Target CPU: 70%
- Min containers: 2
- Max containers: 10
- Scale-out cooldown: 300s

## 🔒 Security Features

### Content Moderation
- Real-time filtering of inappropriate content
- Logging of flagged requests
- User session tracking

### Network Security
- VPC isolation
- Security groups
- ALB with SSL termination
- Private subnets for containers

## 💰 Cost Optimization

### ECS Fargate Pricing
- vCPU: $0.04048 per hour
- Memory: $0.004445 per GB per hour
- Estimated: ~$30-50/month for moderate usage

### Additional Costs
- ALB: ~$16/month
- ECR: $0.10/GB/month
- CloudWatch: Minimal

## 🔧 Configuration

### Environment Variables
```bash
# Required
ASTRA_DB_APPLICATION_TOKEN=your_token
ASTRA_DB_API_ENDPOINT=your_endpoint  
GROQ_API_KEY=your_key

# Optional
SERPER_API_KEY=your_serper_key
COLLECTION_NAME=semantic_data
EMBEDDING_DIMENSION=1536
```

### Model Configuration
- Default: Groq Llama-3.1-8b-instant
- Switchable to OpenAI, Anthropic, etc.
- Configurable via environment variables

## 🎯 Access Your Application

After deployment, access your app at:
- **Load Balancer**: `http://your-alb-dns-name`
- **Custom Domain**: `https://your-domain.com`

## 📈 Usage Analytics

Monitor via CloudWatch:
- Daily active users
- Query volume
- Response times
- Error rates
- Content moderation flags

## 🛠️ Troubleshooting

### Common Issues
1. **Service won't start**: Check CloudWatch logs
2. **502 Bad Gateway**: Health check failing
3. **403 Forbidden**: Check security groups
4. **Memory issues**: Increase task definition memory

### Health Endpoints
- `/health` - Service health
- `/` - Main application
- ALB health checks on port 8000

---
**🚀 Your RAG application is now production-ready and globally accessible!**