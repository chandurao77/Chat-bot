import time, uuid
from typing import Optional
from qdrant_client import AsyncQdrantClient, models
from app.config import settings
from app.core.embeddings import get_embedding
async def _ensure(client):
    names = [c.name for c in (await client.get_collections()).collections]
    if settings.qdrant_semantic_cache_collection not in names:
        await client.create_collection(
            collection_name=settings.qdrant_semantic_cache_collection,
            vectors_config=models.VectorParams(size=768, distance=models.Distance.COSINE))
async def cache_lookup(question: str) -> Optional[dict]:
    client = AsyncQdrantClient(url=settings.qdrant_url)
    await _ensure(client)
    vec = await get_embedding(question)
    res = await client.query_points(collection_name=settings.qdrant_semantic_cache_collection,
        query=vec, limit=1, score_threshold=settings.semantic_cache_threshold)
    await client.close()
    if not res.points: return None
    payload = res.points[0].payload or {}
    if time.time() - payload.get("cached_at", 0) > settings.semantic_cache_ttl_minutes*60: return None
    return payload
async def cache_store(question: str, answer: str, sources: list):
    client = AsyncQdrantClient(url=settings.qdrant_url)
    await _ensure(client)
    vec = await get_embedding(question)
    await client.upsert(collection_name=settings.qdrant_semantic_cache_collection,
        points=[models.PointStruct(id=str(uuid.uuid4()), vector=vec,
            payload={"question": question,"answer": answer,"sources": sources,"cached_at": time.time()})])
    await client.close()
async def invalidate_cache():
    client = AsyncQdrantClient(url=settings.qdrant_url)
    names = [c.name for c in (await client.get_collections()).collections]
    if settings.qdrant_semantic_cache_collection in names:
        await client.delete_collection(settings.qdrant_semantic_cache_collection)
    await client.close()
