# Production RAG Application - Quick Start

## 🚀 Starting the Server

```bash
python start_server.py
```

The server will start at: **http://localhost:8000**

## 📱 Using the Application

1. **Access the Interface**: Open http://localhost:8000 in your browser
2. **Upload Documents**: Click "Choose File" and select a PDF
3. **Ask Questions**: Type your question and click "Ask Question"
4. **Follow-up Questions**: The system remembers conversation context
5. **Clear Session**: Click "Clear Conversation" to start fresh

## ⚡ Features Available

- ✅ **File Upload**: PDF documents are automatically processed
- ✅ **Q&A Interface**: Ask questions about your documents
- ✅ **Conversation Memory**: Follow-up questions work seamlessly
- ✅ **Web Search Fallback**: Gets answers even if not in documents
- ✅ **Generation Pipeline**: AI-powered responses using Groq
- ✅ **Model Switching**: Easy to change models/providers

## 🔧 How It Works

1. **Upload** → PDF is saved to `data/` folder
2. **Ingestion** → Document is chunked and processed
3. **Retrieval** → Search existing knowledge first
4. **Generation** → AI generates precise answers
5. **Memory** → Context preserved for follow-ups
6. **Fallback** → Web search if no documents match

## 📊 System Health

Check system status: http://localhost:8000/health

## 🛑 Stopping the Server

Press `Ctrl+C` in the terminal where the server is running.

---
**Ready for AWS deployment!** 🚀