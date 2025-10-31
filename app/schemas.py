# app/schemas/rag_schemas.py
from __future__ import annotations
from typing import List, Optional
from datetime import date, time
from pydantic import BaseModel, EmailStr, Field

class Message(BaseModel):
    role: str = Field(..., description="either 'user' or 'assistant'")
    text: str

class ConverseRequest(BaseModel):
    user_message: str
    conversation_id: Optional[str] = None
    top_k: int = 5  # number of chunks to retrieve
    temperature: float = 0.2

class ConverseResponse(BaseModel):
    conversation_id: str
    assistant_message: str
    retrieved_chunks: List[str]
    metadata: Optional[dict] = None

class BookingCreate(BaseModel):
    name: str
    email: EmailStr
    date: date
    time: time

class BookingOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    date: date
    time: time
    created_at: Optional[str]
