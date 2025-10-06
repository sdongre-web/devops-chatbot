from fastapi import FastAPI
from contextlib import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from models.schemas import QueryRequest
from services.llm_service import ask_llm
import uvicorn


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    from config import ensure_collection
    ensure_collection()
    print("✅ Qdrant collection ready")
    yield
    # Shutdown (if needed)
    pass
app = FastAPI(title="RAG QnA Backend")

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----------- ROUTES -----------
@app.get("/")
def root():
    """Health check endpoint."""
    return {"message": "RAG Backend is running 🚀"}


@app.post("/query")
def query_api(req: QueryRequest):
    """Main Q&A route."""
    result = ask_llm(req.question, req.top_k)
    return result

@app.post("/data_ingest")
def ingest_data():
    """Ingest data from SQL to Qdrant."""
    from services.data_ingestion_service import ingest_sql_data
    ingest_sql_data()
    return {"message": "Data ingestion completed."}

# ----------- RUN -----------
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
