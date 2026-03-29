import pytest
from unittest.mock import AsyncMock, MagicMock, patch

@pytest.mark.asyncio
async def test_creates():
    mc = AsyncMock(); mc.get_collections.return_value = MagicMock(collections=[])
    with patch("app.core.vector_store.AsyncQdrantClient", return_value=mc):
        from app.core.vector_store import ensure_collection
        await ensure_collection()
    mc.create_collection.assert_called_once()

@pytest.mark.asyncio
async def test_skips():
    mc = AsyncMock(); col = MagicMock(); col.name = "confluence_docs"
    mc.get_collections.return_value = MagicMock(collections=[col])
    with patch("app.core.vector_store.AsyncQdrantClient", return_value=mc), \
         patch("app.core.vector_store.settings") as ms:
        ms.qdrant_url="x"; ms.qdrant_collection="confluence_docs"; ms.upsert_batch_size=100
        from app.core.vector_store import ensure_collection
        await ensure_collection()
    mc.create_collection.assert_not_called()

@pytest.mark.asyncio
async def test_search():
    mc = AsyncMock(); mc.query_points.return_value = MagicMock(points=[MagicMock()])
    with patch("app.core.vector_store.AsyncQdrantClient", return_value=mc):
        from app.core.vector_store import search
        assert len(await search([0.1]*768)) == 1

@pytest.mark.asyncio
async def test_count():
    mc = AsyncMock(); mc.get_collection.return_value = MagicMock(points_count=42)
    with patch("app.core.vector_store.AsyncQdrantClient", return_value=mc):
        from app.core.vector_store import get_collection_count
        assert await get_collection_count() == 42
