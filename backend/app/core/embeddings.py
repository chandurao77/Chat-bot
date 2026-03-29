import httpx, time, asyncio
from typing import List, Dict, Tuple
from app.config import settings
_cache: Dict[str, Tuple[List[float], float]] = {}
async def get_embedding(text: str) -> List[float]:
    now = time.time()
    if text in _cache:
        vec, ts = _cache[text]
        if now - ts < settings.embed_cache_ttl_seconds: return vec
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(f"{settings.ollama_base_url}/api/embeddings",
            json={"model": settings.ollama_embed_model, "prompt": text})
        resp.raise_for_status()
        vec = resp.json()["embedding"]
    _cache[text] = (vec, now)
    for k in [k for k,(_, t) in list(_cache.items()) if now-t > settings.embed_cache_ttl_seconds]:
        del _cache[k]
    return vec
async def get_embeddings_batch(texts: List[str]) -> List[List[float]]:
    results = []
    for i in range(0, len(texts), settings.embed_batch_size):
        vecs = await asyncio.gather(*[get_embedding(t) for t in texts[i:i+settings.embed_batch_size]])
        results.extend(vecs)
    return results
