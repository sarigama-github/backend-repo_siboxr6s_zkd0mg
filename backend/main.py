from __future__ import annotations

from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from database import connect_to_mongo, close_mongo_connection, create_document, get_documents
from schemas import ChatMessage, ChatSession, Track, HealthEntry

app = FastAPI(title="Xuby API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    await connect_to_mongo()


@app.on_event("shutdown")
async def shutdown_event():
    await close_mongo_connection()


class CreateChatSessionRequest(BaseModel):
    user_id: str
    title: str


@app.post("/chat/sessions")
async def create_chat_session(req: CreateChatSessionRequest):
    session = ChatSession(user_id=req.user_id, title=req.title, messages=[])
    doc = await create_document("chatsession", session.model_dump())
    return doc


class AddMessageRequest(BaseModel):
    session_id: str
    role: str
    content: str


@app.post("/chat/message")
async def add_chat_message(req: AddMessageRequest):
    # For demo, store standalone chat message records with session reference
    msg = ChatMessage(role=req.role, content=req.content)
    doc = await create_document("chatmessage", {"session_id": req.session_id, **msg.model_dump()})
    return doc


@app.get("/chat/messages")
async def list_chat_messages(session_id: Optional[str] = None, limit: int = 50):
    filter_dict = {"session_id": session_id} if session_id else None
    docs = await get_documents("chatmessage", filter_dict, limit)
    return {"items": docs}


class CreateTrackRequest(BaseModel):
    title: str
    artist: str
    url: Optional[str] = None


@app.post("/music/tracks")
async def add_track(req: CreateTrackRequest):
    track = Track(title=req.title, artist=req.artist, url=req.url)
    doc = await create_document("track", track.model_dump())
    return doc


@app.get("/music/tracks")
async def list_tracks(limit: int = 50):
    docs = await get_documents("track", None, limit)
    return {"items": docs}


class HealthEntryRequest(BaseModel):
    user_id: str
    type: str
    value: float
    unit: Optional[str] = None


@app.post("/health/entries")
async def add_health_entry(req: HealthEntryRequest):
    entry = HealthEntry(user_id=req.user_id, type=req.type, value=req.value, unit=req.unit)
    doc = await create_document("healthentry", entry.model_dump())
    return doc


@app.get("/health/entries")
async def list_health_entries(user_id: Optional[str] = None, limit: int = 50):
    filter_dict = {"user_id": user_id} if user_id else None
    docs = await get_documents("healthentry", filter_dict, limit)
    return {"items": docs}


@app.get("/test")
async def test():
    # Simple test to verify server and DB connectivity path
    await connect_to_mongo()
    return {"status": "ok"}
