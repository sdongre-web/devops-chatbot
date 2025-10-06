from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
import google.generativeai as genai
from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv
import uvicorn


# ----------- CONFIG -----------
load_dotenv()
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
QDRANT_URL = "http://localhost:6333"
COLLECTION_NAME = "documents"


# ----------- MODEL SETUP -----------
print("📥 Loading embedding model...")
embedder = SentenceTransformer("../all-MiniLM-L6-v2")
print("✅ Embedding model loaded")


if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    llm_model = genai.GenerativeModel("gemini-2.0-flash")
else:
    llm_model = None
    print("⚠️ GEMINI_API_KEY not found!")


# ----------- QDRANT SETUP -----------
qdrant = QdrantClient(QDRANT_URL)
collections = qdrant.get_collections().collections
if COLLECTION_NAME not in [c.name for c in collections]:
    qdrant.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=models.VectorParams(
            size=384, 
            distance=models.Distance.COSINE
        ),
    )


# ----------- FASTAPI APP -----------
app = FastAPI(title="RAG QnA Backend")


# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ----------- MODELS -----------
class QueryRequest(BaseModel):
    question: str
    top_k: int = 3


# ----------- HELPER FUNCTIONS -----------
def query_documents(query: str, top_k: int = 3):
    """Query Qdrant for relevant documents based on vector similarity."""
    query_vector = embedder.encode(query).tolist()
    results = qdrant.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k,
    )
    # Return documents with their scores
    return [(point.payload["text"], point.score) for point in results.points]


def ask_llm(question: str, top_k: int = 3):
    """
    Generate an answer using Gemini LLM with retrieved context.
    Falls back to general knowledge if no relevant documents are found.
    """
    docs_with_scores = query_documents(question, top_k)
    
    if not llm_model:
        return {"answer": "Gemini API not configured.", "source": "error"}

    # Check if we have relevant documents (score threshold)
    relevant_docs = [doc for doc, score in docs_with_scores if score > 0.3]
    
    if relevant_docs:
        # We have relevant context from database
        context = "\n\n".join(
            [f"Document {i+1}:\n{doc}" for i, doc in enumerate(relevant_docs)]
        )
        
        prompt = f"""You are a helpful DevOps assistant. Answer the question based on the provided context from our internal knowledge base.


        Context from Knowledge Base:
        {context}

        Question: {question}

        IMPORTANT FORMATTING INSTRUCTIONS:
        - Use markdown formatting for clarity and structure
        - For code examples, ALWAYS use proper code blocks with language tags:
        - Use bold for important terms, concepts, or key points
        - Use inline code for commands, file names, variables, or technical terms
        - Use ## for main section headers (sparingly)
        - Use ### for subsection headers if needed
        - Use bullet points with • for lists
        - Use numbered lists (1. 2. 3.) for sequential steps or procedures
        - Keep explanations clear and concise
        - Add blank lines between sections for readability

        Answer:
    """
        try:
            response = llm_model.generate_content(prompt)
            return {"answer": response.text, "source": "database"}
        except Exception as e:
            return {"answer": f"Error generating response: {e}", "source": "error"}
    else:
        
        # No relevant documents found, use LLM's general knowledge
        prompt = f"""You are a helpful DevOps assistant. The user asked a question but we don't have specific information about it in our internal knowledge base.

        Question: {question}

        IMPORTANT FORMATTING INSTRUCTIONS:
        - Use markdown formatting for clarity and structure
        - For code examples, ALWAYS use proper code blocks with language tags:
        - Use bold for important terms, concepts, or key points
        - Use inline code for commands, file names, variables, or technical terms
        - Use ## for main section headers (sparingly)
        - Use ### for subsection headers if needed
        - Use bullet points with • for lists
        - Use numbered lists (1. 2. 3.) for sequential steps or procedures
        - Keep explanations clear and concise
        - Be helpful and accurate
        - If you're not sure, say so

        Answer:
        """
        try:
            response = llm_model.generate_content(prompt)
            return {"answer": response.text, "source": "llm_knowledge"}
        except Exception as e:
            return {"answer": f"Error generating response: {e}", "source": "error"}


# ----------- API ROUTES -----------
@app.post("/query")
def query_api(req: QueryRequest):
    """
    Query endpoint that accepts a question and returns an AI-generated answer.
    """
    result = ask_llm(req.question, req.top_k)
    return result


@app.get("/")
def root():
    """Health check endpoint."""
    return {"message": "RAG Backend is running 🚀"}


# ----------- RUN SERVER -----------
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
