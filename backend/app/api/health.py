import aiosqlite, httpx
from fastapi import APIRouter
from app.config import settings
from app.core.vector_store import get_collection_count
router = APIRouter()
@router.get("/health")
async def health_check():
    status = {"status":"ok","components":{}}
    for name, url in [("qdrant",f"{settings.qdrant_url}/healthz"),("ollama",settings.ollama_base_url)]:
        try:
            async with httpx.AsyncClient(timeout=5) as c: r = await c.get(url)
            status["components"][name] = "ok" if r.status_code==200 else "degraded"
        except Exception: status["components"][name] = "unreachable"
    try:
        async with aiosqlite.connect(settings.sqlite_path) as db: await db.execute("SELECT 1")
        status["components"]["sqlite"] = "ok"
    except Exception: status["components"]["sqlite"] = "error"
    return status
@router.get("/health/metrics")
async def metrics():
    async with aiosqlite.connect(settings.sqlite_path) as db:
        async with db.execute("SELECT COUNT(*) FROM messages WHERE role='user'") as cur:
            total = (await cur.fetchone())[0]
        async with db.execute("SELECT COUNT(*) FROM feedback WHERE vote=-1") as cur:
            neg = (await cur.fetchone())[0]
    return {"total_queries":total,"no_answer_rate":round(neg/max(total,1),3),
            "indexed_documents": await get_collection_count()}
@router.get("/health/spaces")
async def ingested_spaces():
    async with aiosqlite.connect(settings.sqlite_path) as db:
        async with db.execute("SELECT DISTINCT space_key FROM page_index") as cur:
            rows = await cur.fetchall()
    return {"spaces":[r[0] for r in rows]}
