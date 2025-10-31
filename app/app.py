import os
import tempfile
from datetime import date, time
from contextlib import asynccontextmanager
from fastapi import FastAPI, File, UploadFile, Form, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.db import Metadata, create_db_and_tables, get_async_session, Booking
from .utils.chunking import chunk_file_delimiter, chunk_file_fixed
from .utils.embeddings import store_embeddings_in_qdrant
from .utils.redis_memory import RedisMemory, get_redis_memory
from .utils.rag_service import (
    embed_text_for_query,
    retrieve_relevant_chunks,
    generate_answer,
    SYSTEM_PROMPT,
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_db_and_tables()
    yield

app = FastAPI(lifespan=lifespan)

# ---- File Upload Endpoint ----
@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    session: AsyncSession = Depends(get_async_session),
    strategy: str = Form("fixed"),
    chunk_size: int = Form(500),
    delimiter: str = Form("\n\n"),
    overlap: int = Form(0),
):
    suffix = os.path.splitext(file.filename)[-1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        tmp_path = tmp.name

    try:
        if strategy == "fixed":
            chunks = chunk_file_fixed(tmp_path, chunk_size, overlap)
        elif strategy == "delimiter":
            chunks = chunk_file_delimiter(tmp_path, delimiter)
        else:
            return JSONResponse(
                content={"error": "Invalid strategy. Choose 'fixed' or 'delimiter'."},
                status_code=400,
            )

        store_embeddings_in_qdrant(chunks)
        metadata = Metadata(file_name=file.filename, file_size=f"{(file.size / 1024):.2f}KiB")
        session.add(metadata)
        await session.commit()
        await session.refresh(metadata)
        return {
            "filename": file.filename,
            "total_chunks": len(chunks),
            "size": f"{(file.size / 1024):.2f}KiB",
        }
    finally:
        os.remove(tmp_path)

# ---- Conversational RAG ----
@app.post("/converse")
async def converse(
    user_message: str = Form(...),
    conversation_id: Optional[str] = Form(None),
    top_k: int = Form(5),
    session: AsyncSession = Depends(get_async_session),
    redis_memory: RedisMemory = Depends(get_redis_memory),
):
    conv_id = conversation_id or await redis_memory.create_conversation_id()
    await redis_memory.append_message(conv_id, "user", user_message)
    query_embedding = await embed_text_for_query(user_message)
    chunks = await retrieve_relevant_chunks(query_embedding, top_k)
    conversation = await redis_memory.get_messages(conv_id)
    answer = await generate_answer(SYSTEM_PROMPT, conversation, chunks, user_message)
    await redis_memory.append_message(conv_id, "assistant", answer)
    return {"conversation_id": conv_id, "assistant_message": answer, "retrieved_chunks": chunks}

@app.get("/memory/{conversation_id}")
async def get_memory(conversation_id: str, redis_memory: RedisMemory = Depends(get_redis_memory)):
    messages = await redis_memory.get_messages(conversation_id)
    if not messages:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return messages

# ---- Interview Booking ----
@app.post("/book_interview", status_code=status.HTTP_201_CREATED)
async def book_interview(
    name: str = Form(...),
    email: str = Form(...),
    date: date = Form(...),
    time: time = Form(...),
    session: AsyncSession = Depends(get_async_session),
):
    new_booking = Booking(name=name, email=email, date=date, time=time)
    session.add(new_booking)
    await session.commit()
    await session.refresh(new_booking)
    return new_booking

@app.get("/bookings")
async def list_bookings(session: AsyncSession = Depends(get_async_session)):
    result = await session.execute(text("SELECT id, name, email, date, time, created_at FROM bookings ORDER BY created_at DESC"))
    rows = result.fetchall()
    return [
        {"id": r[0], "name": r[1], "email": r[2], "date": r[3], "time": r[4], "created_at": r[5]}
        for r in rows
    ]
