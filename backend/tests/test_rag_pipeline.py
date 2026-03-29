import pytest
from unittest.mock import AsyncMock, patch, MagicMock

@pytest.mark.asyncio
async def test_cache_hit():
    cached = {"answer":"Cached","sources":[],"cached_at":9e18}
    with patch("app.core.rag_pipeline.cache_lookup", new_callable=AsyncMock, return_value=cached):
        from app.core.rag_pipeline import run_rag
        events = [e async for e in run_rag("q", [], "c")]
    assert any(e["type"]=="token" for e in events)
    assert any(e["type"]=="done" for e in events)

@pytest.mark.asyncio
async def test_tokens():
    mp = MagicMock()
    mp.payload = {"page_id":"p1","title":"T","space_key":"DEV","space_name":"D","url":"","content":"c"}
    mp.score = 0.5
    async def fake(_): yield "T1"; yield "T2"
    with patch("app.core.rag_pipeline.cache_lookup", new_callable=AsyncMock, return_value=None), \
         patch("app.core.rag_pipeline.get_embedding", new_callable=AsyncMock, return_value=[0.1]*768), \
         patch("app.core.rag_pipeline.search", new_callable=AsyncMock, return_value=[mp]), \
         patch("app.core.rag_pipeline.expand_context", new_callable=AsyncMock, return_value=[]), \
         patch("app.core.rag_pipeline.cache_store", new_callable=AsyncMock), \
         patch("app.core.rag_pipeline.stream_llm", side_effect=lambda m: fake(m)):
        from app.core.rag_pipeline import run_rag
        tokens = [e["data"] for e in [e async for e in run_rag("q",[],  "c")] if e["type"]=="token"]
    assert "T1" in tokens and "T2" in tokens

@pytest.mark.asyncio
async def test_sources():
    mp = MagicMock()
    mp.payload = {"page_id":"p1","title":"T","space_key":"DEV","space_name":"D","url":"","content":"c"}
    mp.score = 0.6
    async def fake(_): yield "A"
    with patch("app.core.rag_pipeline.cache_lookup", new_callable=AsyncMock, return_value=None), \
         patch("app.core.rag_pipeline.get_embedding", new_callable=AsyncMock, return_value=[0.1]*768), \
         patch("app.core.rag_pipeline.search", new_callable=AsyncMock, return_value=[mp]), \
         patch("app.core.rag_pipeline.expand_context", new_callable=AsyncMock, return_value=[]), \
         patch("app.core.rag_pipeline.cache_store", new_callable=AsyncMock), \
         patch("app.core.rag_pipeline.stream_llm", side_effect=lambda m: fake(m)):
        from app.core.rag_pipeline import run_rag
        events = [e async for e in run_rag("q", [], "c")]
    assert any(e["type"]=="sources" for e in events)
