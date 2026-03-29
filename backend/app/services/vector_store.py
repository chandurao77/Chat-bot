from typing import List
from qdrant_client import AsyncQdrantClient, models
from app.config import settings

VECTOR_DIM = 768

async def ensure_collection():
    client = AsyncQdrantClient(url=settings.qdrant_url)
    names = [c.name for c in (await client.get_collections()).collections]
    if settings.qdrant_collection not in names:
        await client.create_collection(
            collection_name=settings.qdrant_collection,
            vectors_config=models.VectorParams(size=VECTOR_DIM, distance=models.Distance.COSINE,
                hnsw_config=models.HnswConfigDiff(m=16, ef_construct=100)))
        await client.create_payload_index(settings.qdrant_collection, "title",
            models.PayloadSchemaType.KEYWORD)
        await client.create_payload_index(settings.qdrant_collection, "content",
            models.PayloadSchemaType.TEXT)
    await client.close()

async def hybrid_search(query_vec: List[float], query_text: str, top_k: int = 10,
                        score_threshold: float = 0.30) -> list:
    client = AsyncQdrantClient(url=settings.qdrant_url)
    # Vector search
    vec_results = await client.query_points(
        collection_name=settings.qdrant_collection,
        query=query_vec, limit=top_k, score_threshold=score_threshold)
    # Keyword search on title
    kw_title = await client.query_points(
        collection_name=settings.qdrant_collection,
        query=query_vec, limit=top_k,
        query_filter=models.Filter(must=[models.FieldCondition(key="title",
            match=models.MatchText(text=query_text))]))
    # Keyword search on content
    kw_content = await client.query_points(
        collection_name=settings.qdrant_collection,
        query=query_vec, limit=top_k,
        query_filter=models.Filter(must=[models.FieldCondition(key="content",
            match=models.MatchText(text=query_text))]))
    await client.close()
    # Merge by score
    seen, merged = {}, []
    for point in vec_results.points:
        seen[point.id] = point.score
        merged.append(point)
    for point in (*kw_title.points, *kw_content.points):
        if point.id not in seen:
            seen[point.id] = point.score * 0.65
            merged.append(point)
    merged.sort(key=lambda p: seen[p.id], reverse=True)
    return merged[:top_k]

async def search_by_page_ids(page_ids: List[str]) -> list:
    client = AsyncQdrantClient(url=settings.qdrant_url)
    results, _ = await client.scroll(
        collection_name=settings.qdrant_collection,
        scroll_filter=models.Filter(must=[models.FieldCondition(key="page_id",
            match=models.MatchAny(any=page_ids))]),
        limit=settings.graph_max_expansion * 2)
    await client.close()
    return results

async def upsert_points(points: list):
    client = AsyncQdrantClient(url=settings.qdrant_url)
    for i in range(0, len(points), settings.upsert_batch_size):
        await client.upsert(collection_name=settings.qdrant_collection,
            points=points[i:i + settings.upsert_batch_size])
    await client.close()

async def get_collection_count() -> int:
    client = AsyncQdrantClient(url=settings.qdrant_url)
    try:
        count = (await client.get_collection(settings.qdrant_collection)).points_count or 0
    except Exception: count = 0
    await client.close()
    return count
