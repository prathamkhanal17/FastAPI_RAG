from qdrant_client import QdrantClient
from qdrant_client.http import models
from sentence_transformers import SentenceTransformer
import uuid

model = SentenceTransformer("all-MiniLM-L6-v2")

client = QdrantClient("http://localhost:6333")

def store_embeddings_in_qdrant(chunks, collection_name="documents_collection"):
    """
    Generate embeddings for given text chunks and store them in Qdrant.
    Each chunk has:
    - vector embedding
    - text payload
    """

    # Create or ensure collection exists
    client.recreate_collection(
        collection_name=collection_name,
        vectors_config=models.VectorParams(
            size=model.get_sentence_embedding_dimension(),
            distance=models.Distance.COSINE
        )
    )

    # Generate embeddings
    embeddings = model.encode(chunks).tolist()

    # Prepare and upsert
    points = [
        models.PointStruct(
            id=str(uuid.uuid4()),
            vector=vector,
            payload={"text": chunk}
        )
        for chunk, vector in zip(chunks, embeddings)
    ]

    client.upsert(collection_name=collection_name, points=points)
    print(f"Stored {len(points)} chunks in Qdrant collection '{collection_name}'")
    return {"collection": collection_name, "stored_chunks": len(points)}
