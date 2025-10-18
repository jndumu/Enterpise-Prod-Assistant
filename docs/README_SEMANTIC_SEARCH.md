# Groq-Powered Semantic Search System

## Overview
Production-ready semantic search system using **Groq** as the default AI provider, with AstraDB for vector storage and web search fallback.

## System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   User Query    │ => │  MCP Client      │ => │  Response       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────┐
                       │ AstraDB     │
                       │ Search      │
                       └─────────────┘
                              │ (if no results)
                              ▼
                       ┌─────────────┐    ┌─────────────┐
                       │ Web Search  │ => │ Groq        │
                       │ (Fallback)  │    │ Summary     │
                       └─────────────┘    └─────────────┘
```

## Features

✅ **Groq Integration**: Uses Groq's `llama-3.1-8b-instant` model by default
✅ **Semantic Search**: AstraDB vector search with automatic fallback
✅ **Web Search Fallback**: Intelligent web search when no relevant data found
✅ **REST API**: FastAPI server with WebSocket support
✅ **Production Ready**: Error handling, logging, async support
✅ **No Hallucination**: Only uses retrieved data or web search results

## Quick Start

### 1. Environment Setup
```bash
# Required environment variables in .env
ASTRA_DB_APPLICATION_TOKEN="your_astra_token"
ASTRA_DB_API_ENDPOINT="your_astra_endpoint"
GROQ_API_KEY="your_groq_api_key"

# Optional
GOOGLE_API_KEY="your_google_api_key"
GOOGLE_SEARCH_ENGINE_ID="your_search_engine_id"
```

### 2. Install Dependencies
```bash
pip install groq astrapy requests beautifulsoup4 fastapi uvicorn python-dotenv
```

### 3. Test the System
```bash
# Run comprehensive tests
python test_app.py

# Run demo
python demo.py
```

### 4. Start the Server
```bash
# Start FastAPI server
python -m mcp.server
```

## Usage Examples

### Direct Usage
```python
from mcp import MCPClient

# Initialize with Groq
client = MCPClient(provider="groq")

# Ask questions
result = client.query("What is machine learning?")
print(f"Answer: {result['answer']}")
print(f"Source: {result['source']}")  # 'astradb' or 'web_search'
```

### Server API
```bash
# Health check
curl http://localhost:8000/health

# Query endpoint
curl -X POST http://localhost:8000/query \
  -H "Content-Type: application/json" \
  -d '{"question": "What is Python?"}'
```

### WebSocket
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');
ws.send(JSON.stringify({
  type: "query",
  question: "Explain neural networks",
  threshold: 0.7
}));
```

## File Structure
```
├── retriever/
│   ├── __init__.py
│   └── retrieval.py        # AstraDB semantic search
├── mcp/
│   ├── __init__.py
│   ├── web_search.py       # Groq-powered web search
│   ├── client.py           # MCP orchestrator
│   └── server.py           # FastAPI server
├── test_app.py            # Comprehensive tests
├── demo.py                # Interactive demo
└── README_SEMANTIC_SEARCH.md
```

## How It Works

1. **User submits query** to MCP Client
2. **AstraDB search** first - if relevant results found (score ≥ 0.7), return them
3. **Web search fallback** - if no AstraDB results, search the web
4. **Groq summarization** - uses Groq to create concise, factual summaries
5. **Structured response** - returns answer with source attribution

## Configuration

### AI Provider Settings
```python
# Use Groq (default)
client = MCPClient(provider="groq")

# Use OpenAI (if available)
client = MCPClient(provider="openai", api_key="sk-...")
```

### Search Thresholds
```python
# Adjust relevance threshold
client.relevance_threshold = 0.8  # Higher = more strict
```

## Production Deployment

### Environment Variables
- `ASTRA_DB_APPLICATION_TOKEN`: Required
- `ASTRA_DB_API_ENDPOINT`: Required  
- `GROQ_API_KEY`: Required for AI features
- `GOOGLE_API_KEY`: Optional for Google search
- `GOOGLE_SEARCH_ENGINE_ID`: Optional for Google search

### Server Configuration
```python
# Start server
server = MCPServer(
    provider="groq",
    host="0.0.0.0",
    port=8000
)
server.run()
```

## API Endpoints

- `GET /` - Server status
- `GET /health` - Health check with component status
- `POST /query` - Single query
- `POST /batch-query` - Multiple queries
- `WebSocket /ws` - Real-time queries

## Demo Results

The system successfully:
- ✅ Initializes Groq client
- ✅ Generates mock web search results  
- ✅ Creates AI-powered summaries using Groq
- ✅ Falls back gracefully when AstraDB collection doesn't exist
- ✅ Provides factual answers with source attribution

## Support

The system is designed to work with your existing .env configuration and uses Groq as the preferred AI provider for fast, cost-effective language processing.