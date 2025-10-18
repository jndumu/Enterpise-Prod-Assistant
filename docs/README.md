# Production RAG Application 🚀

A production-ready Retrieval-Augmented Generation (RAG) system that combines document knowledge with real-time web search, featuring AI-powered responses, conversation memory, and content moderation.

## 🌟 Features

- **📄 Document Processing**: Upload and process PDF documents with automatic chunking and embedding
- **🔍 Multi-Source Search**: Combines document search with real-time web search (Serper, Wikipedia, DuckDuckGo)
- **🤖 AI Generation**: Context-aware responses using Groq LLM with conversation memory
- **🛡️ Content Moderation**: Built-in safety guardrails to prevent inappropriate usage
- **💬 Conversation Memory**: Maintains context across follow-up questions
- **🌐 Web Interface**: Clean, responsive UI for document upload and Q&A
- **☁️ Cloud Ready**: Fully containerized with AWS deployment automation

## 🏗️ Architecture

```mermaid
graph TB
    A[Web Interface] --> B[FastAPI Server]
    B --> C[Content Moderation]
    C --> D[Memory Manager]
    D --> E[MCP Client]
    E --> F[Document Retrieval]
    E --> G[Web Search]
    F --> H[AstraDB Vector Store]
    G --> I[Serper API]
    G --> J[Wikipedia API] 
    G --> K[DuckDuckGo API]
    E --> L[Response Generation]
    L --> M[Groq LLM]
    
    N[Document Upload] --> O[Ingestion Pipeline]
    O --> P[PDF Processing]
    P --> Q[Text Chunking]
    Q --> R[Embedding Generation]
    R --> H
```

### Core Components

- **Frontend**: HTML/JavaScript interface with file upload and chat
- **Backend**: FastAPI server with REST API endpoints
- **Retrieval**: Multi-source search combining documents and web
- **Generation**: AI-powered response synthesis with Groq
- **Memory**: Conversation context management
- **Moderation**: Content safety and inappropriate usage prevention
- **Storage**: AstraDB for vector embeddings and document chunks

## 📋 Prerequisites

### Required Services
1. **AstraDB Account** (for vector storage)
2. **Groq API Key** (for AI generation)
3. **AWS Account** (for deployment)
4. **GitHub Account** (for CI/CD)

### Optional Services (Recommended)
- **Serper API Key** (for real-time Google search)
- **Custom Domain** (for production URL)

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone <your-repo-url>
cd rag-application
```

### 2. Environment Setup
Create `.env` file in the root directory:
```bash
# Required - AstraDB Configuration
ASTRA_DB_APPLICATION_TOKEN=AstraCS:your_token_here
ASTRA_DB_API_ENDPOINT=https://your-db-id-region.apps.astra.datastax.com
COLLECTION_NAME=semantic_data
EMBEDDING_DIMENSION=1536

# Required - AI Generation
GROQ_API_KEY=gsk_your_groq_api_key_here

# Optional - Enhanced Web Search
SERPER_API_KEY=your_serper_api_key_here

# Optional - Configuration
ASTRA_DB_KEYSPACE=default_keyspace
```

### 3. Local Development
```bash
# Install dependencies
pip install -r requirements.txt

# Run the application
python main_app.py
```

Access the application at `http://localhost:8000`

### 4. Upload Documents
1. Visit the web interface
2. Click "Choose File" and select a PDF
3. Click "Upload & Process"
4. Wait for processing confirmation

### 5. Ask Questions
1. Type your question in the text area
2. Click "Ask Question"
3. Get AI-generated responses with sources
4. Ask follow-up questions for context-aware conversations

## 🔧 Configuration Guide

### AstraDB Setup
1. **Create Account**: Sign up at [astra.datastax.com](https://astra.datastax.com)
2. **Create Database**: 
   - Choose "Serverless (Vector)" 
   - Select region closest to your users
   - Note the Database ID and Region
3. **Generate Token**:
   - Go to "Settings" → "Application Tokens"
   - Create new token with "Database Administrator" role
   - Save the token securely
4. **Get API Endpoint**:
   - Format: `https://DATABASE_ID-REGION.apps.astra.datastax.com`
   - Find in database "Connect" tab

### Groq API Setup
1. **Create Account**: Visit [console.groq.com](https://console.groq.com)
2. **Generate API Key**:
   - Navigate to "API Keys"
   - Create new key
   - Copy and store securely
3. **Model Access**: Ensure access to `llama-3.1-8b-instant`

### Serper API Setup (Optional)
1. **Create Account**: Visit [serper.dev](https://serper.dev)
2. **Get API Key**:
   - Sign up for free tier (2,500 searches/month)
   - Copy API key from dashboard
3. **Benefits**: Real-time Google search results for current information

## 🛠️ Development

### Project Structure
```
rag-application/
├── app/                    # Core application
│   ├── api/               # FastAPI routes and endpoints
│   ├── core/              # Memory, moderation, optimization
│   ├── services/          # Retrieval, generation, ingestion
│   └── models/            # Data models and schemas
├── frontend/              # Web interface
│   ├── templates/         # HTML templates
│   └── static/           # CSS, JavaScript, images
├── infrastructure/        # AWS infrastructure as code
├── .github/workflows/     # CI/CD automation
├── data/                 # Document storage (local)
├── scripts/              # Utility scripts
├── tests/                # Test files
├── main_app.py          # Application entry point
├── Dockerfile           # Container configuration
├── requirements.txt     # Python dependencies
└── .env                 # Environment variables (create this)
```

### Key Files
- `main_app.py`: FastAPI application with all endpoints
- `app/services/client.py`: Main orchestration client
- `app/services/generation.py`: AI response generation
- `app/core/memory.py`: Conversation context management
- `app/core/moderation.py`: Content safety filters
- `app/services/enhanced_web_search.py`: Multi-source web search

### Running Tests
```bash
# Test individual components
python -c "from app.core.moderation import moderate_user_input; print('✅ Moderation working')"
python -c "from app.services.enhanced_web_search import EnhancedWebSearch; print('✅ Search working')"

# Test complete pipeline
python -c "from app.services.client import MCPClient; client=MCPClient(); print(client.health_check())"
```

## 🌐 Deployment

### GitHub Secrets Configuration

Set up these secrets in your GitHub repository (`Settings > Secrets and variables > Actions`):

#### Required AWS Secrets
```
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
```

#### Required Application Secrets
```
ASTRA_DB_APPLICATION_TOKEN=AstraCS:BcDeFgHiJkL...
ASTRA_DB_API_ENDPOINT=https://12345678-1234-1234-1234-123456789abc-us-east1.apps.astra.datastax.com
GROQ_API_KEY=gsk_AbCdEfGhIjKlMnOpQrStUvWxYz1234567890
```

#### Optional Secrets (Recommended)
```
SERPER_API_KEY=1234567890abcdef1234567890abcdef12345678
COLLECTION_NAME=semantic_data
EMBEDDING_DIMENSION=1536
```

### AWS Prerequisites

1. **IAM User with Permissions**:
   - `AmazonECS_FullAccess`
   - `AmazonEC2ContainerRegistryFullAccess`
   - `IAMFullAccess`
   - `AmazonVPCFullAccess`
   - `ElasticLoadBalancingFullAccess`

2. **AWS CLI Configuration** (for local testing):
   ```bash
   aws configure
   # Enter your access key, secret key, region (us-east-1), output format (json)
   ```

### Infrastructure Deployment

1. **Deploy Infrastructure**:
   ```bash
   cd infrastructure
   terraform init
   terraform plan
   terraform apply
   ```

2. **Note Output**: Save the Load Balancer DNS name from Terraform output

### Application Deployment

#### Automatic (Recommended)
1. **Push to Main**: Deployment triggers automatically
   ```bash
   git add .
   git commit -m "Deploy production RAG app"
   git push origin main
   ```

2. **Monitor Deployment**: Check GitHub Actions tab for progress

3. **Access Application**: Use ALB DNS name from Terraform output

#### Manual Deployment
```bash
# Build and push Docker image
docker build -t rag-app .
docker tag rag-app:latest $ECR_URI:latest  
docker push $ECR_URI:latest

# Update ECS service
aws ecs update-service --cluster rag-app-cluster --service rag-app-service --force-new-deployment
```

## 📊 Usage Examples

### Basic Document Q&A
1. **Upload**: Upload a PDF about machine learning
2. **Query**: "What is supervised learning?"
3. **Response**: AI-generated answer based on document content

### Follow-up Questions
1. **Initial**: "What are neural networks?"
2. **Follow-up**: "How do they learn?"
3. **Context-Aware**: System remembers previous conversation

### Current Information
1. **Query**: "Who is the current president of the United States?"
2. **Web Search**: Falls back to real-time web search
3. **Source Attribution**: Shows search sources used

### Content Moderation
1. **Inappropriate Query**: System blocks and provides gentle guidance
2. **Harmful Requests**: Prevents dangerous or illegal activities
3. **Educational Focus**: Encourages constructive usage

## 🔍 API Endpoints

### Core Endpoints
- `GET /`: Web interface
- `POST /upload`: File upload and processing
- `POST /query`: Question answering with memory
- `GET /health`: System health check
- `DELETE /sessions/{id}`: Clear conversation memory

### Example API Usage
```python
import requests

# Upload document
files = {'file': open('document.pdf', 'rb')}
response = requests.post('http://localhost:8000/upload', files=files)

# Ask question
data = {
    'question': 'What is the main topic?',
    'session_id': 'user123'
}
response = requests.post('http://localhost:8000/query', data=data)
print(response.json())
```

## 🛡️ Security & Compliance

### Content Moderation
- **Real-time filtering** of inappropriate language
- **Harmful content detection** prevents dangerous requests
- **Request logging** for compliance monitoring
- **Educational guardrails** encourage proper usage

### Data Security
- **Environment variables** for sensitive configuration
- **VPC isolation** in AWS deployment
- **HTTPS encryption** for all communication
- **No data persistence** of user conversations (optional)

### Privacy
- **Session-based memory** (not permanently stored)
- **No user authentication** required (stateless)
- **Document privacy** (uploaded files processed locally)
- **API key security** (stored in environment variables)

## 📈 Monitoring & Analytics

### Health Monitoring
- **Application health**: `/health` endpoint
- **Database connectivity**: AstraDB connection status
- **API availability**: External service status checks
- **Resource usage**: Memory and CPU metrics

### CloudWatch Metrics (AWS)
- **Request volume**: Queries per minute/hour
- **Response times**: API endpoint latency
- **Error rates**: Failed requests and causes
- **Scaling events**: Auto-scaling triggers

### Content Analytics
- **Query patterns**: Most common question types
- **Source distribution**: Document vs web search usage
- **Moderation flags**: Inappropriate usage attempts
- **Session lengths**: Average conversation duration

## 💰 Cost Optimization

### Estimated AWS Costs (Monthly)
- **ECS Fargate**: $30-50 (2 containers, moderate usage)
- **Application Load Balancer**: $16
- **ECR Repository**: $1-2
- **CloudWatch Logs**: $2-5
- **Data Transfer**: $5-10
- **Total**: ~$55-85/month

### External API Costs
- **Groq**: Free tier includes 14,400 requests/day
- **Serper**: Free tier includes 2,500 searches/month
- **AstraDB**: Free tier includes 5GB storage
- **Scaling**: All services have pay-as-you-go pricing

### Cost Reduction Tips
1. **Use free tiers** during development
2. **Monitor usage** via service dashboards
3. **Set billing alerts** for unexpected costs
4. **Scale down** non-production environments

## 🚨 Troubleshooting

### Common Issues

#### Application Won't Start
```bash
# Check logs
docker logs <container_id>

# Verify environment variables
python -c "import os; print(os.getenv('GROQ_API_KEY')[:10])"

# Test database connection
python -c "from app.services.client import MCPClient; print(MCPClient().health_check())"
```

#### Upload Failing
- **Check file size**: PDFs should be < 100MB
- **Verify format**: Only PDF files supported
- **Check permissions**: Ensure `data/` directory is writable
- **Monitor logs**: Check server logs for processing errors

#### Queries Not Working
- **Test moderation**: Ensure query passes content filters
- **Check APIs**: Verify Groq and search API keys
- **Database status**: Confirm AstraDB connectivity
- **Memory issues**: Clear session if needed

#### AWS Deployment Issues
- **ECR permissions**: Ensure GitHub Actions can push
- **ECS service**: Check service status in AWS console
- **Load balancer**: Verify health checks passing
- **Security groups**: Confirm port 8000 is open

### Getting Help
1. **Check logs**: Application and infrastructure logs
2. **GitHub Issues**: Report bugs and feature requests
3. **Documentation**: Review this README and deployment guide
4. **Community**: Join discussions in repository

## 🤝 Contributing

### Development Setup
```bash
# Fork repository
git fork <repo-url>

# Clone your fork
git clone <your-fork-url>
cd rag-application

# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and test
python -m pytest tests/

# Commit and push
git commit -m "Add your feature"
git push origin feature/your-feature-name
```

### Code Standards
- **Python**: Follow PEP 8 style guide
- **Line length**: Maximum 100 lines per file
- **Documentation**: Update README for new features
- **Testing**: Add tests for new functionality

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **AstraDB**: Vector database platform
- **Groq**: High-performance AI inference
- **FastAPI**: Modern Python web framework
- **AWS**: Cloud infrastructure platform
- **Open Source Community**: Libraries and tools used

---

## 🆘 Quick Help

**Need immediate help?** 

1. **Environment Issues**: Check `.env` file configuration
2. **API Errors**: Verify all API keys are valid and have sufficient quotas
3. **Database Issues**: Confirm AstraDB collection exists and is accessible
4. **Deployment Problems**: Check GitHub Actions logs and AWS CloudWatch

**Common Commands:**
```bash
# Local development
python main_app.py

# Test health
curl http://localhost:8000/health

# Check logs
docker logs $(docker ps -q)

# Deploy to AWS
git push origin main
```

**🚀 Ready to build your production RAG system!**