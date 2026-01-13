# Regulatory Compliance Assistant - RAG Application

A sophisticated AI-powered Regulatory Compliance Assistant built using Retrieval-Augmented Generation (RAG) architecture. This application provides intelligent, conversational compliance guidance by combining large language models with a comprehensive regulatory document knowledge base.

## 🎯 Overview

The Regulatory Compliance Assistant transforms complex regulatory compliance queries into natural, conversational interactions. It analyzes compliance documents, provides accurate assessments, and maintains context across multi-turn conversations—all while citing specific regulatory sources.

### Key Features

- **🤖 Conversational AI Agent**: Natural language interactions powered by Llama 3.3 70B via Groq
- **📚 Document Intelligence**: RAG-based retrieval using FAISS vector store with sentence transformers
- **💬 Context-Aware Conversations**: Maintains conversation history for follow-up questions and clarifications
- **🎯 Compliance Assessment**: Provides structured compliance status (Compliant/Non-Compliant/Needs Review)
- **📖 Source Citations**: Every response includes references to specific regulatory documents
- **🔍 Smart Query Classification**: Distinguishes between initial queries, follow-ups, clarifications, and expansions
- **⚡ Real-time Responses**: Fast inference with optimized token management
- **🎨 Modern UI**: Clean, ChatGPT-inspired interface built with React and Tailwind CSS

---

## 🏗️ Architecture

### Technology Stack

#### Backend
- **Framework**: FastAPI (Python 3.11+)
- **LLM**: Llama 3.3 70B Versatile (via Groq API)
- **Vector Store**: FAISS with Sentence Transformers (`all-MiniLM-L6-v2`)
- **Document Processing**: LangChain Community
- **Database**: MongoDB (conversation history)
- **Embeddings**: Sentence Transformers
- **Token Management**: Custom token manager with tiktoken

#### Frontend
- **Framework**: React 18 with Vite
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **HTTP Client**: Axios
- **State Management**: React Hooks

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         User Interface                       │
│                    (React + Tailwind CSS)                    │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│                      FastAPI Backend                         │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Query Endpoint                          │   │
│  │  • Session Management                                │   │
│  │  • History Retrieval (20 messages)                   │   │
│  │  • Response Formatting                               │   │
│  └──────────────────┬───────────────────────────────────┘   │
│                     │                                        │
│                     ▼                                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │          Compliance Agent (LangChain)                │   │
│  │  • Prompt Engineering                                │   │
│  │  • Context Assembly                                  │   │
│  │  • LLM Orchestration                                 │   │
│  │  • Response Parsing                                  │   │
│  └──────┬───────────────────────────────────┬───────────┘   │
│         │                                   │               │
│         ▼                                   ▼               │
│  ┌─────────────────┐              ┌──────────────────┐     │
│  │  Vector Store   │              │   Groq LLM API   │     │
│  │  (FAISS Index)  │              │  (Llama 3.3 70B) │     │
│  │  • Embeddings   │              │  • Inference     │     │
│  │  • Similarity   │              │  • JSON Output   │     │
│  └─────────────────┘              └──────────────────┘     │
│         │                                                    │
│         ▼                                                    │
│  ┌─────────────────────────────────────────────────────┐   │
│  │          MongoDB (Chat History)                     │   │
│  │  • Session Storage                                  │   │
│  │  • Conversation Context                             │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🚀 Getting Started

### Prerequisites

- **Python**: 3.11 or higher
- **Node.js**: 18.x or higher
- **MongoDB**: 4.4 or higher (running locally or remote)
- **Groq API Key**: Get one from [console.groq.com](https://console.groq.com)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/arvindpandey4/regulatory_compliance_assistant.git
   cd regulatory_compliance_assistant
   ```

2. **Backend Setup**
   ```bash
   cd backend
   python -m venv venv
   .\venv\Scripts\Activate.ps1  # Windows
   # source venv/bin/activate    # Linux/Mac
   
   pip install -r requirements.txt
   ```

3. **Configure Environment Variables**
   
   Create `backend/.env`:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   MONGODB_URL=mongodb://localhost:27017
   ```

4. **Ingest Regulatory Documents**
   
   Place your PDF documents in `backend/data/documents/` and run:
   ```bash
   # The vector store will be created automatically on first run
   # Or use the ingestion endpoint via API
   ```

5. **Frontend Setup**
   ```bash
   cd ../frontend
   npm install
   ```

### Running the Application

#### Option 1: Run All Services (Recommended)
```bash
# From project root
.\run-all.ps1
```

This starts:
- Backend API: `http://127.0.0.1:8000`
- Frontend UI: `http://localhost:5173`
- API Docs: `http://127.0.0.1:8000/docs`

#### Option 2: Run Services Separately

**Backend:**
```bash
cd backend
.\run.ps1
# Or: uvicorn main:app --reload
```

**Frontend:**
```bash
cd frontend
npm run dev
```

### Stopping the Application

```bash
# From project root
.\stop-all.ps1
```

This safely terminates all processes and prevents unnecessary API token usage.

---

## 📖 Usage

### Basic Workflow

1. **Open the Application**: Navigate to `http://localhost:5173`

2. **Ask a Compliance Question**:
   ```
   "Does our data retention policy comply with GDPR Article 5?"
   ```

3. **Review the Response**:
   - **Conversational Answer**: Natural language response
   - **Compliance Status**: Compliant/Non-Compliant/Needs Review
   - **Technical Details**: Expandable detailed analysis
   - **Sources**: Referenced regulatory documents

4. **Follow-up Questions**:
   ```
   "Can you expand on the data minimization principle?"
   "What did you mean by retention periods?"
   "Tell me more about the requirements"
   ```

### Query Types

The agent intelligently handles different query types:

| Type | Example | Response Style |
|------|---------|---------------|
| **Analysis** | "Is our policy compliant with GDPR?" | Full compliance assessment with status, reasoning, and sources |
| **Follow-up** | "Tell me more about that" | Builds on previous context, conversational |
| **Clarification** | "What does data minimization mean?" | Direct explanation, references prior discussion |
| **Expansion** | "Can you expand on retention periods?" | Detailed analysis of specific topic |

---

## 🔧 API Documentation

### Endpoints

#### `POST /api/v1/query/`
Submit a compliance query and receive an AI-generated response.

**Request:**
```json
{
  "query": "Does our policy comply with GDPR?",
  "session_id": "optional-session-id"
}
```

**Response:**
```json
{
  "session_id": "uuid-v4",
  "data": {
    "response": "Based on the regulatory documents...",
    "status": "Compliant",
    "reasoning": "Detailed technical analysis...",
    "relevant_clauses": ["GDPR Article 5(1)(e)", "..."],
    "sources": [
      {
        "document_name": "GDPR_Compliance_Guide.pdf",
        "excerpt": "Relevant text excerpt...",
        "relevance_score": 0.92
      }
    ],
    "conversation_type": "analysis"
  }
}
```

#### `POST /api/v1/ingest/`
Upload and process new regulatory documents.

**Request:**
```bash
curl -X POST "http://127.0.0.1:8000/api/v1/ingest/" \
  -F "file=@document.pdf"
```

#### `GET /api/v1/health/`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "vector_store": "loaded",
  "documents": 42
}
```

---

## 🧪 Testing

### Test the API

```bash
cd backend
python test_api_live.py
```

This script tests:
- Initial compliance queries
- Follow-up questions
- Session management
- Response structure validation

### Manual Testing

Use the interactive API documentation:
```
http://127.0.0.1:8000/docs
```

---

## 📁 Project Structure

```
regulatory_compliance_assistant/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── endpoints/
│   │   │   │   ├── query.py          # Main query endpoint
│   │   │   │   ├── ingestion.py      # Document upload
│   │   │   │   └── health.py         # Health checks
│   │   │   └── routes.py             # API router
│   │   ├── core/
│   │   │   ├── config.py             # Configuration
│   │   │   ├── database.py           # MongoDB connection
│   │   │   ├── middleware.py         # Logging middleware
│   │   │   └── token_manager.py      # Token limit management
│   │   ├── models/
│   │   │   └── schemas.py            # Pydantic models
│   │   └── services/
│   │       ├── agent.py              # Compliance agent (core logic)
│   │       ├── chat_history.py       # Conversation management
│   │       ├── document_processor.py # PDF processing
│   │       └── vector_store.py       # FAISS vector store
│   ├── data/
│   │   ├── documents/                # Source PDFs
│   │   └── vector_store/             # FAISS index
│   ├── main.py                       # FastAPI app
│   ├── requirements.txt              # Python dependencies
│   ├── .env                          # Environment variables
│   └── test_api_live.py              # API test script
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   └── ChatInterface.jsx     # Main chat UI
│   │   ├── services/
│   │   │   └── api.js                # API client
│   │   ├── App.jsx                   # Root component
│   │   └── main.jsx                  # Entry point
│   ├── public/
│   ├── package.json                  # Node dependencies
│   └── vite.config.js                # Vite configuration
├── run-all.ps1                       # Start all services
├── stop-all.ps1                      # Stop all services
└── README.md                         # This file
```

---

## 🎨 Features Deep Dive

### 1. Conversational Intelligence

The agent maintains context across conversations:
- **Session Management**: Each conversation has a unique session ID
- **History Tracking**: Last 20 messages stored in MongoDB
- **Context Assembly**: Previous exchanges inform current responses
- **Smart Routing**: Detects query type and adjusts response style

### 2. Compliance Assessment

Structured compliance analysis:
- **Status Classification**: Compliant, Non-Compliant, Needs Review
- **Reasoning**: Detailed technical explanation
- **Clause Identification**: Specific regulatory references
- **Source Citations**: Document excerpts with relevance scores

### 3. Document Processing

Intelligent document handling:
- **PDF Parsing**: Extracts text from regulatory PDFs
- **Chunking**: Splits documents into semantic chunks
- **Embedding**: Converts chunks to vector embeddings
- **Indexing**: Stores in FAISS for fast similarity search

### 4. Token Management

Optimized for cost and performance:
- **Context Truncation**: Manages token limits intelligently
- **Priority System**: Keeps query and recent history, truncates older context
- **Token Counting**: Uses tiktoken for accurate counting
- **Budget Awareness**: Prevents exceeding model limits

### 5. Error Handling

Robust fallback mechanisms:
- **JSON Parsing**: Handles markdown-wrapped responses
- **Schema Validation**: Graceful handling of missing fields
- **Fallback Responses**: User-friendly error messages
- **Detailed Logging**: Comprehensive error tracking

---

## 🔐 Security & Best Practices

- **API Key Protection**: `.env` files are gitignored
- **Input Validation**: Pydantic schemas validate all inputs
- **CORS Configuration**: Configurable allowed origins
- **Error Sanitization**: Sensitive details not exposed to frontend
- **Session Isolation**: Each conversation is independently tracked

---

## 🚧 Troubleshooting

### Common Issues

**1. "Rate limit exceeded" error**
- **Cause**: Groq API daily token limit reached
- **Solution**: Wait for limit reset or upgrade Groq tier

**2. Vector store not loading**
- **Cause**: Missing or corrupted FAISS index
- **Solution**: Delete `backend/data/vector_store/` and re-ingest documents

**3. MongoDB connection failed**
- **Cause**: MongoDB not running
- **Solution**: Start MongoDB service: `mongod`

**4. Port already in use**
- **Cause**: Previous process still running
- **Solution**: Run `.\stop-all.ps1` or manually kill processes

**5. Frontend can't connect to backend**
- **Cause**: Backend not running or CORS issue
- **Solution**: Ensure backend is running on port 8000, check CORS settings

---

## 📊 Performance

- **Query Response Time**: ~1-3 seconds (including LLM inference)
- **Vector Search**: <100ms for 1000+ documents
- **Concurrent Users**: Supports multiple simultaneous sessions
- **Token Usage**: ~500-2000 tokens per query (depending on context)

---

## 🛣️ Roadmap

### Planned Features

- [ ] **Streaming Responses**: Real-time token-by-token output
- [ ] **Multi-document Upload**: Batch ingestion via UI
- [ ] **Export Conversations**: Download as PDF compliance reports
- [ ] **Advanced Search**: Filter by document, date, compliance status
- [ ] **User Authentication**: Multi-user support with role-based access
- [ ] **Analytics Dashboard**: Query trends, compliance insights
- [ ] **Custom Embeddings**: Fine-tuned models for regulatory text
- [ ] **Multilingual Support**: Compliance guidance in multiple languages

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

## 👤 Author

**Arvind Pandey**

- GitHub: [@arvindpandey4](https://github.com/arvindpandey4)
- Project: [Regulatory Compliance Assistant](https://github.com/arvindpandey4/regulatory_compliance_assistant)

---

## 🙏 Acknowledgments

- **Groq**: For providing fast LLM inference
- **LangChain**: For RAG orchestration framework
- **FAISS**: For efficient vector similarity search
- **FastAPI**: For the high-performance backend framework
- **React**: For the modern, responsive UI

---

## 📞 Support

For issues, questions, or suggestions:
- Open an issue on [GitHub Issues](https://github.com/arvindpandey4/regulatory_compliance_assistant/issues)
- Check the [API Documentation](http://127.0.0.1:8000/docs) when running locally

---

**Built with ❤️ for better compliance management**
