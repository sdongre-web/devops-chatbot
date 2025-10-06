from sentence_transformers import SentenceTransformer

print("📥 Loading embedding model...")
# embedder = SentenceTransformer("C:\\Users\\parvej.korabu\\Desktop\\Chatbot\\all-MiniLM-L6-v2")
embedder = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

print("✅ Embedding model loaded")
