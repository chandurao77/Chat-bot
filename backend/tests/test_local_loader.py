import pytest, json
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_txt(tmp_path):
    (tmp_path/"t.txt").write_text("Hello world. This is test.")
    with patch("app.ingestion.local_loader.settings") as ms, \
         patch("app.ingestion.local_loader.ensure_collection", new_callable=AsyncMock), \
         patch("app.ingestion.local_loader.get_embeddings_batch", new_callable=AsyncMock, return_value=[[0.1]*768]), \
         patch("app.ingestion.local_loader.upsert_points", new_callable=AsyncMock), \
         patch("app.ingestion.local_loader.invalidate_cache", new_callable=AsyncMock):
        ms.local_docs_path=str(tmp_path); ms.chunk_size_words=512; ms.chunk_overlap_words=64
        from app.ingestion.local_loader import ingest_local
        assert await ingest_local() >= 1

@pytest.mark.asyncio
async def test_md(tmp_path):
    (tmp_path/"r.md").write_text("# Title\nContent here.")
    with patch("app.ingestion.local_loader.settings") as ms, \
         patch("app.ingestion.local_loader.ensure_collection", new_callable=AsyncMock), \
         patch("app.ingestion.local_loader.get_embeddings_batch", new_callable=AsyncMock, return_value=[[0.1]*768]), \
         patch("app.ingestion.local_loader.upsert_points", new_callable=AsyncMock), \
         patch("app.ingestion.local_loader.invalidate_cache", new_callable=AsyncMock):
        ms.local_docs_path=str(tmp_path); ms.chunk_size_words=512; ms.chunk_overlap_words=64
        from app.ingestion.local_loader import ingest_local
        assert await ingest_local() >= 1

@pytest.mark.asyncio
async def test_json(tmp_path):
    (tmp_path/"d.json").write_text(json.dumps({"k":"v","info":"doc text"}))
    with patch("app.ingestion.local_loader.settings") as ms, \
         patch("app.ingestion.local_loader.ensure_collection", new_callable=AsyncMock), \
         patch("app.ingestion.local_loader.get_embeddings_batch", new_callable=AsyncMock, return_value=[[0.1]*768]), \
         patch("app.ingestion.local_loader.upsert_points", new_callable=AsyncMock), \
         patch("app.ingestion.local_loader.invalidate_cache", new_callable=AsyncMock):
        ms.local_docs_path=str(tmp_path); ms.chunk_size_words=512; ms.chunk_overlap_words=64
        from app.ingestion.local_loader import ingest_local
        assert await ingest_local() >= 1
