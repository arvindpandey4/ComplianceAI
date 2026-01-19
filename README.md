# Regulatory Compliance Assistant - RAG Application

A sophisticated AI-powered Regulatory Compliance Assistant built using specific Agentic  architecture. This application provides intelligent, conversational compliance guidance by combining large language models with a comprehensive regulatory document knowledge base.

## 🎯 Overview

The Regulatory Compliance Assistant transforms complex regulatory compliance queries into natural, conversational interactions. It analyzes compliance documents, provides accurate assessments, and maintains context across multi-turn conversations—all while citing specific regulatory sources.

### Key Features

- **🤖 Conversational AI Agent**: Natural language interactions powered by **PydanticAI** and Llama 3.3 70B (Groq) with Fallback to OpenRouter.
- **📚 Document Intelligence**: RAG-based retrieval using FAISS vector store with sentence transformers.
- **⚡ Fast Track Retrieval**: Instant answers from a curated **Golden Knowledge Base** for high-confidence matches.
- **🧠 Dynamic Reranking**: Advanced relevance scoring (**FlashRank**) to prioritize the best context.
- **🎯 Strict Compliance Assessment**: Provides structured compliance status (Compliant/Non-Compliant/Needs Review) using strict **Pydantic** output validation.
- **🔍 Smart Orchestration**: Distinguishes between initial queries, follow-ups, and clarifications using intelligent routing.
- **💬 Context-Aware Conversations**: Maintains conversation history for follow-up questions in MongoDB.
- **📖 Source Citations**: Every response includes references to specific regulatory documents.
- **🎨 Modern UI**: Clean, ChatGPT-inspired interface built with React + Vite + Tailwind CSS.

---

## 🏗️ Architecture

### Technology Stack

#### Backend
- **Framework**: FastAPI (Python 3.11+)
- **Agent Framework**: **PydanticAI** (Agentic Workflow & Validation)
- **Primary LLM**: Llama 3.3 70B Versatile (via Groq API)
- **Fallback LLM**: Gemini/OpenAI (via OpenRouter API - Free Tier)
- **Vector Store**: FAISS with Sentence Transformers (`all-MiniLM-L6-v2`)
- **Reranker**: FlashRank (Cross-Encoder)
- **Database**: MongoDB (Conversation History) / Atlas
- **Validation**: Pydantic (Strict Schema Enforcement)
- **Logging**: Loguru + Correlation ID Tracking

#### Frontend
- **Framework**: React 18 with Vite
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **HTTP Client**: Axios
- **State Management**: React Hooks

### System Diagram

```mermaid
graph TD
    %% =========================
    %% Client / UI Layer
    %% =========================
    Client[CompliancAI Web Client<br/>(React + Vite + Tailwind)] <-->|REST API (JSON)<br/>/api/v1/query| API[FastAPI Backend<br/>(Python 3.11+)]
    Client <-->|Upload PDF (multipart)<br/>/api/v1/ingest| API
    Client <-->|Health Check<br/>/api/v1/health| API

    %% =========================
    %% Persistence / Storage
    %% =========================
    API <-->|Read/Write Sessions<br/>Chat History| Mongo[(MongoDB / Atlas)]
    API -->|Read Golden KB<br/>fast-track Q&A| GoldenKB[(Golden Knowledge Base<br/>JSON Store)]
    API -->|Read Follow-up KB| FollowupKB[(Follow-up Questions KB<br/>JSON Store)]

    %% =========================
    %% Agent System (PydanticAI)
    %% =========================
    subgraph AgentOrchestration[PydanticAI Agent Orchestration]
        Router[Query Router<br/>Classification + Fast-Track Gate] -->|If fast-track match| FastTrack[Fast-Track Answer Builder]
        Router -->|Else: Retrieval Pipeline| Retrieve[Context Retrieval Tool<br/>(FAISS Similarity Search)]
        Retrieve --> Rerank[Re-ranking Tool<br/>(FlashRank)]
        Rerank --> ContextPack[Context Assembly<br/>Top-K Chunks + Metadata]
        ContextPack --> Agent[PydanticAI Compliance Agent<br/>(Strict Output Schema)]
        Agent --> Validate[Schema Validation<br/>(Pydantic Result Model)]
        Validate --> Followups[Follow-up Generator<br/>(Context-aware Qs)]
    end

    API -->|Invoke| Router

    %% =========================
    %% Retrieval Components
    %% =========================
    subgraph RetrievalLayer[RAG Retrieval Layer]
        FAISS[(FAISS Vector Store<br/>Index + Doc Chunks)]
        Embeddings[Sentence Transformers<br/>(all-MiniLM-L6-v2)]
        Docs[(Regulatory PDF Corpus<br/>/data/documents)]
    end

    API -->|Search Top-N| FAISS
    Docs -->|Chunk + Embed| Embeddings
    Embeddings -->|Vectors| FAISS

    %% =========================
    %% LLM Providers + Fallback
    %% =========================
    subgraph ModelLayer[LLM Providers (Primary + Fallback)]
        Groq[Groq API<br/>Llama 3.3 70B]
        OpenRouter[OpenRouter API<br/>Free/Low-Cost Model Fallback]
    end

    Agent -->|Primary Inference| Groq
    Agent -->|Fallback on timeout/429/errors| OpenRouter

    %% =========================
    %% Observability / Reliability
    %% =========================
    subgraph Reliability[Production Reliability]
        Logs[Structured Logging<br/>JSON + Correlation IDs]
        Retry[Retries + Timeouts<br/>Backoff Strategy]
        SafeErrors[Error Sanitization<br/>Consistent API Errors]
        RateLimit[Rate Limiting<br/>Per IP/Session]
    end

    API --> Logs
    API --> Retry
    API --> SafeErrors
    API --> RateLimit

    %% =========================
    %% Response Contract
    %% =========================
    subgraph Response[Response Output Contract]
        Output[JSON Response<br/>response + status + reasoning<br/>relevant_clauses + sources[]<br/>conversation_type + followup_questions]
    end

    Validate --> Output
    Output -->|Return to Client| Client

    %% =========================
    %% Deployment Targets
    %% =========================
    subgraph Deployment[Live Deployment]
        WebHost[Frontend Hosting<br/>Vercel / Netlify]
        APIHost[Backend Hosting<br/>Render / Railway / Fly.io]
        DBHost[MongoDB Atlas<br/>(Managed)]
    end

    Client --> WebHost
    API --> APIHost
    Mongo --> DBHost
```

---

## 🚀 Getting Started

### Prerequisites

- **Python**: 3.11 or higher
- **Node.js**: 18.x or higher
- **MongoDB**: 4.4+ (Local or Atlas)
- **Groq API Key**: Get one from [console.groq.com](https://console.groq.com)
- **OpenRouter API Key** (Optional): For fallback support.

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
   OPENROUTER_API_KEY=your_openrouter_key_here
   MONGODB_URL=mongodb://localhost:27017
   ```

4. **Ingest Knowledge Base** (Optional but Recommended)
   ```bash
   # Ingest the Golden Knowledge Base (Fast Track):
   cd backend
   python ingest_kb.py
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
.\venv\Scripts\Activate.ps1
.\run.ps1
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
This safely terminates all processes and releases the ports.

---

## 📖 Usage

1. **Open the Application**: Navigate to `http://localhost:5173`.
2. **Analysis Mode**: Ask complex questions like "Does our data retention policy comply with GDPR Article 5?". The agent will use RAG to retrieve documents and provide a formal assessment.
3. **Fast-Track Mode**: Ask common questions like "What is the maximum fine under GDPR?". If the answer exists in the Golden KB, you'll get an instant, pre-verified response.
4. **Follow-up**: Click suggested questions or ask your own to dig deeper.

---

## 🔧 API Documentation

**Interactive Docs**: `http://127.0.0.1:8000/docs`

#### `POST /api/v1/query/`
Submit a compliance query. The PydanticAI agent orchestrates the response.

**Request:**
```json
{
  "query": "Does our policy comply with GDPR?",
  "session_id": "optional-session-id"
}
```

**Response (Strict Schema):**
```json
{
  "session_id": "uuid-v4",
  "data": {
    "response": "Based on the regulatory documents...",
    "status": "Compliant|Non-Compliant|Needs Review",
    "reasoning": "Detailed technical analysis...",
    "relevant_clauses": ["GDPR Article 5(1)(e)"],
    "sources": [
      { "document_name": "GDPR_Guide.pdf", "excerpt": "...", "relevance_score": 0.92 }
    ],
    "conversation_type": "analysis",
    "follow_up_questions": ["What about data minimisation?"]
  }
}
```

---

## 🤝 Contributing

Contributions are welcome! Please follow these guidelines:
1. Fork the repository.
2. Create a feature branch.
3. Commit your changes.
4. Push to the branch.
5. Open a Pull Request.

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

- **Groq**: For providing fast LLM inference.
- **PydanticAI**: For the robust agentic framework.
- **LangChain & FAISS**: For RAG foundational components.
- **FlashRank**: For ensuring high-quality retrieval.
