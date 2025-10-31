# FastAPI

This repository implements a modular backend using FastAPI, Qdrant, Redis, and Transformers.

## Features
- Document ingestion with recursive/fixed chunking
- Embeddings with SentenceTransformers
- Qdrant vector database integration
- Custom conversational RAG pipeline (no RetrievalQAChain)
- Redis chat memory
- Interview booking API

## Quickstart
1. Install uv
2. Start Redis and Qdrant (docker)
3. uv run ./main.py
