import pytest, time
from unittest.mock import AsyncMock, MagicMock, patch

@pytest.mark.asyncio
async def test_miss():
    mc = AsyncMock()
    mc.get_collections.return_value = MagicMock(collections=[])
    mc.query_points.return_value = MagicMock(points=[])
    with patch("app.core.semantic_cache.AsyncQdrantClient", return_value=mc), \
         patch("app.core.semantic_cache.get_embedding", new_callable=AsyncMock, return_value=[0.1]*768):
        from app.core.semantic_cache import cache_lookup
        assert await cache_lookup("q") is None

@pytest.mark.asyncio
async def test_hit():
    mp = MagicMock()
    mp.payload = {"question":"q","answer":"a","sources":[],"cached_at":time.time()}
    mc = AsyncMock()
    mc.get_collections.return_value = MagicMock(collections=[MagicMock(name="semantic_cache")])
    mc.query_points.return_value = MagicMock(points=[mp])
    with patch("app.core.semantic_cache.AsyncQdrantClient", return_value=mc), \
         patch("app.core.semantic_cache.get_embedding", new_callable=AsyncMock, return_value=[0.1]*768), \
         patch("app.core.semantic_cache.settings") as ms:
        ms.qdrant_url="x"; ms.qdrant_semantic_cache_collection="semantic_cache"
        ms.semantic_cache_threshold=0.95; ms.semantic_cache_ttl_minutes=30
        from app.core.semantic_cache import cache_lookup
        r = await cache_lookup("q")
    assert r is not None and r["answer"]=="a"

@pytest.mark.asyncio
async def test_expired():
    mp = MagicMock()
    mp.payload = {"question":"q","answer":"a","sources":[],"cached_at":0}
    mc = AsyncMock()
    mc.get_collections.return_value = MagicMock(collections=[MagicMock(name="semantic_cache")])
    mc.query_points.return_value = MagicMock(points=[mp])
    with patch("app.core.semantic_cache.AsyncQdrantClient", return_value=mc), \
         patch("app.core.semantic_cache.get_embedding", new_callable=AsyncMock, return_value=[0.1]*768), \
         patch("app.core.semantic_cache.settings") as ms:
        ms.qdrant_url="x"; ms.qdrant_semantic_cache_collection="semantic_cache"
        ms.semantic_cache_threshold=0.95; ms.semantic_cache_ttl_minutes=30
        from app.core.semantic_cache import cache_lookup
        assert await cache_lookup("q") is None
