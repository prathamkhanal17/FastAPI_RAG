import os
import openai
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    print("API key is not set")
openai.api_key = OPENAI_API_KEY

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

qdrant_client = QdrantClient("http://localhost:6333")

