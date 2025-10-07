# AI DevOps Copilot

AI-powered chatbot for DevOps teams, combining RAG (Retrieval-Augmented Generation) with LLMs and internal documentation search.  
Supports Q&A, code snippets, and integration with SQL, Qdrant, and Gemini LLM.

## Features

- **FastAPI backend** with RAG Q&A endpoints
- **Qdrant vector database** for semantic search
- **Gemini LLM** for natural language answers
- **MySQL integration** for ingesting documentation
- **React + Vite frontend** with chat UI and markdown/code rendering
- **Dockerized** for easy deployment

## Directory Structure

```
AI-DevOps-Copilot/
  backend/
    core/            # Embedding models
    models/          # Pydantic schemas
    services/        # LLM, Qdrant, data ingestion logic
    utils/           # DB connection
    main.py          # FastAPI app
    config.py        # Config & Qdrant setup
    requirements.txt # Python dependencies
    Dockerfile       # Backend container
  frontend/
    src/             # React app source
    public/          # Static assets
    package.json     # Frontend dependencies
    Dockerfile       # Frontend container
    ...
  docker-compose.yml # Multi-service orchestration
  README.md          # Project documentation
```

## Setup & Usage

### Prerequisites

- Docker & Docker Compose
- API keys for Gemini, Qdrant, MySQL, etc.

### 1. Environment Variables

Set required variables in `.env` files or via Docker Compose:

- `GEMINI_API_KEY`
- `QDRANT_URL`
- `DB_HOST`, `DB_USER`, `DB_PASS`, `DB_NAME`
- (see [backend/config.py](backend/config.py))

### 2. Build & Run (Docker Compose)

```sh
docker-compose up --build
```

- Backend: http://HOST-IP:8000
- Frontend: http://HOST-IP:5173

### 3. Data Ingestion

To ingest documentation from MySQL into Qdrant, call:

```sh
curl -X POST http://localhost:8000/data_ingest
```

### 4. Chatbot Usage

- Open the frontend in your browser.
- Ask DevOps questions; the bot will search internal docs and use LLM for answers.
