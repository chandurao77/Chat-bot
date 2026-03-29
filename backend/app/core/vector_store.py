from typing import List
from qdrant_client import AsyncQdrantClient, models
from app.config import settings
VECTOR_DIM = 768
async def ensure_collection():
    client = AsyncQdrantClient(url=settings.qdrant_url)
    names = [c.name for c in (await client.get_collections()).collections]
    if settings.qdrant_collection not in names:
        await client.create_collection(collection_name=settings.qdrant_collection,
            vectors_config=models.VectorParams(size=VECTOR_DIM, distance=models.Distance.COSINE,
                hnsw_config=models.HnswConfigDiff(m=16, ef_construct=100)))
    await client.close()
async def upsert_points(points: list):
    client = AsyncQdrantClient(url=settings.qdrant_url)
    for i in range(0, len(points), settings.upsert_batch_size):
        await client.upsert(collection_name=settings.qdrant_collection,
            points=points[i:i+settings.upsert_batch_size])
    await client.close()
async def search(vector: List[float], top_k=3, score_threshold=0.35) -> list:
    client = AsyncQdrantClient(url=settings.qdrant_url)
    res = await client.query_points(collection_name=settings.qdrant_collection,
        query=vector, limit=top_k, score_threshold=score_threshold)
    await client.close()
    return res.points
async def search_by_page_ids(page_ids: List[str]) -> list:
    client = AsyncQdrantClient(url=settings.qdrant_url)
    results, _ = await client.scroll(collection_name=settings.qdrant_collection,
        scroll_filter=models.Filter(must=[models.FieldCondition(key="page_id",
            match=models.MatchAny(any=page_ids))]),
        limit=settings.graph_rag_max_extra*2)
    await client.close()
    return results
async def get_collection_count() -> int:
    client = AsyncQdrantClient(url=settings.qdrant_url)
    try:
        count = (await client.get_collection(settings.qdrant_collection)).points_count or 0
    except Exception: count = 0
    await client.close()
    return count
