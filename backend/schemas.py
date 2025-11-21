from __future__ import annotations

from typing import Optional, List
from pydantic import BaseModel, Field


class ChatMessage(BaseModel):
    role: str = Field(..., description="sender role: user, assistant, system")
    content: str


class ChatSession(BaseModel):
    user_id: str
    title: str
    messages: List[ChatMessage] = []


class Track(BaseModel):
    title: str
    artist: str
    url: Optional[str] = None


class HealthEntry(BaseModel):
    user_id: str
    type: str = Field(..., description="metric type: steps, sleep, calories, mood, water")
    value: float
    unit: Optional[str] = None
