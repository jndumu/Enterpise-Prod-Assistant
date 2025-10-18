# Enterprise Production Assistant

> AI-powered document Q&A system with web search fallback

## Quick Start

```bash
# Local development
pip install -r requirements.txt
python main.py

# Production deployment
docker build -t enterprise-assistant .
docker run -p 8000:8000 enterprise-assistant
```

## Features

- 📄 PDF document upload and processing
- 🔍 Intelligent document search
- 🌐 Web search fallback via DuckDuckGo
- ⚡ FastAPI with automatic API docs
- 🐳 Production Docker container

## API Endpoints

- `GET /` - Web interface
- `GET /health` - Health check
- `POST /upload` - Document upload
- `POST /query` - Q&A endpoint
- `GET /docs` - API documentation

## Architecture

```
main.py                 # Application (125 lines)
frontend/
├── templates/index.html    # Web interface
└── static/                 # CSS/JS assets
requirements.txt            # Dependencies (7 packages)
Dockerfile                  # Production container
```

## Deployment

**AWS ECS**: http://3.148.172.43:8000

```bash
# Build and deploy
docker build -t enterprise-assistant .
docker tag enterprise-assistant:latest 135334155695.dkr.ecr.us-east-2.amazonaws.com/enterprise-assistant:latest
docker push 135334155695.dkr.ecr.us-east-2.amazonaws.com/enterprise-assistant:latest
aws ecs update-service --cluster enterprise-assistant --service enterprise-assistant-simple-service --force-new-deployment --region us-east-2
```

## Tech Stack

- **Backend**: FastAPI + Uvicorn
- **Document Processing**: PyPDF
- **Frontend**: HTML/CSS/JavaScript
- **Search**: Keyword matching + DuckDuckGo
- **Infrastructure**: AWS ECS Fargate