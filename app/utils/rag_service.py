import os
from qdrant_client import QdrantClient
from sentence_transformers import SentenceTransformer
from openai import AsyncOpenAI
from typing import List

QDRANT_HOST = os.getenv("QDRANT_HOST", "http://localhost:6333")
QDRANT_COLLECTION = "documents_collection"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

qdrant_client = QdrantClient(QDRANT_HOST)
model = SentenceTransformer("all-MiniLM-L6-v2")

SYSTEM_PROMPT = (
    "You are a helpful assistant that answers based on provided document context. "
    "Never hallucinate — if the answer isn't in context, say you don't know."
)

async def embed_text_for_query(text: str) -> List[float]:
    return model.encode([text])[0].tolist()

async def retrieve_relevant_chunks(query_embedding, top_k: int = 5) -> List[str]:
    results = qdrant_client.search(
        collection_name=QDRANT_COLLECTION,
        query_vector=query_embedding,
        limit=top_k,
        with_payload=True
    )
    return [hit.payload.get("text", "") for hit in results]

async def generate_answer(system_prompt: str, conversation: list, context_chunks: list, query: str) -> str:
    client = AsyncOpenAI(api_key=OPENAI_API_KEY)

    context_text = "\n\n".join(context_chunks)
    conversation_text = "\n".join([f"{m['role']}: {m['text']}" for m in conversation[-6:]])

    prompt = (
        f"{system_prompt}\n\n"
        f"Context:\n{context_text}\n\n"
        f"Conversation:\n{conversation_text}\n\n"
        f"User: {query}\n\n"
        "Use only the context to answer. If the context doesn't help, say you don't know."
    )

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
        max_tokens=512
    )

    return response.choices[0].message.content.strip()
    # return "Dummy reply"
