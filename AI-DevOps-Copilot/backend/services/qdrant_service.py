from config import qdrant, COLLECTION_NAME
from core.embeddings import embedder

def query_documents(query: str, top_k: int = 3):
    """Query Qdrant for similar documents."""
    query_vector = embedder.encode(query).tolist()
    results = qdrant.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k,
    )
    return [(point.payload.get("text", ""), point.score) for point in results.points]
