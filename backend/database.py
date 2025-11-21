from __future__ import annotations

import os
from typing import Any, Dict, Optional
from datetime import datetime

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pydantic import BaseModel


class Database:
    client: Optional[AsyncIOMotorClient] = None
    db: Optional[AsyncIOMotorDatabase] = None


db_instance = Database()


def _get_env(name: str, default: Optional[str] = None) -> str:
    value = os.getenv(name, default)
    if value is None:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


async def connect_to_mongo() -> None:
    if db_instance.client is None:
        mongo_url = os.getenv("DATABASE_URL", "mongodb://localhost:27017")
        db_name = os.getenv("DATABASE_NAME", "app_db")
        db_instance.client = AsyncIOMotorClient(mongo_url)
        db_instance.db = db_instance.client[db_name]


async def close_mongo_connection() -> None:
    if db_instance.client is not None:
        db_instance.client.close()
        db_instance.client = None
        db_instance.db = None


async def create_document(collection_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
    if db_instance.db is None:
        await connect_to_mongo()
    assert db_instance.db is not None
    now = datetime.utcnow()
    data_with_meta = {**data, "created_at": now, "updated_at": now}
    result = await db_instance.db[collection_name].insert_one(data_with_meta)
    doc = await db_instance.db[collection_name].find_one({"_id": result.inserted_id})
    if doc and "_id" in doc:
        doc["id"] = str(doc.pop("_id"))
    return doc or {}


async def get_documents(
    collection_name: str,
    filter_dict: Optional[Dict[str, Any]] = None,
    limit: int = 50,
) -> list[Dict[str, Any]]:
    if db_instance.db is None:
        await connect_to_mongo()
    assert db_instance.db is not None
    cursor = db_instance.db[collection_name].find(filter_dict or {}).limit(limit)
    docs = []
    async for d in cursor:
        if "_id" in d:
            d["id"] = str(d.pop("_id"))
        docs.append(d)
    return docs
