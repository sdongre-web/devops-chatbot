# import os
# from dotenv import load_dotenv
# from qdrant_client import QdrantClient
# from qdrant_client.http import models

# # Load env
# load_dotenv()

# # Environment variables
# GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
# QDRANT_URL = "http://localhost:6333"
# COLLECTION_NAME = "documents"

# # Initialize Qdrant client
# qdrant = QdrantClient(QDRANT_URL)

# # Ensure collection exists
# collections = qdrant.get_collections().collections
# if COLLECTION_NAME not in [c.name for c in collections]:
#     qdrant.create_collection(
#         collection_name=COL
import os
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http import models

# Load env
load_dotenv()

# Environment variables
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
COLLECTION_NAME = "documents"

# Initialize Qdrant client (connection happens lazily)
qdrant = QdrantClient(QDRANT_URL)

def ensure_collection():
    """Check and create collection if needed. Call this at startup."""
    try:
        collections = qdrant.get_collections().collections
        if COLLECTION_NAME not in [c.name for c in collections]:
            qdrant.create_collection(
                collection_name=COLLECTION_NAME,
                vectors_config=models.VectorParams(size=384, distance=models.Distance.COSINE),
            )
    except Exception as e:
        print(f"Error ensuring collection: {e}")
        raise