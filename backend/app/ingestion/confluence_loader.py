import asyncio, time, uuid
import aiosqlite, httpx
from typing import List, Optional
from app.config import settings
from app.ingestion.html_parser import parse_html
from app.ingestion.chunker import split_text
from app.core.embeddings import get_embeddings_batch
from app.core.vector_store import ensure_collection, upsert_points
from app.core.semantic_cache import invalidate_cache
from qdrant_client import models
_status = {"running":False,"progress":0,"total":0,"message":"idle"}
def get_status(): return _status
async def ingest_confluence(spaces: Optional[List[str]]=None):
    global _status
    _status = {"running":True,"progress":0,"total":0,"message":"Starting..."}
    await ensure_collection()
    targets = spaces or [s.strip() for s in settings.confluence_spaces.split(",") if s.strip()]
    auth = (settings.confluence_username, settings.confluence_api_token)
    all_pages = []
    async with httpx.AsyncClient(auth=auth, timeout=30) as c:
        for space in targets:
            start = 0
            while True:
                resp = await c.get(f"{settings.confluence_url}/wiki/rest/api/content",
                    params={"spaceKey":space,"type":"page","start":start,"limit":50,
                            "expand":"body.storage,version,space"})
                if resp.status_code==429:
                    await asyncio.sleep(float(resp.headers.get("Retry-After",5))); continue
                resp.raise_for_status()
                data = resp.json(); results = data.get("results",[])
                if not results: break
                for p in results: all_pages.append((p, space))
                if data.get("_links",{}).get("next"): start += 50
                else: break
                await asyncio.sleep(0.1)
    _status["total"] = len(all_pages)
    points = []
    async with aiosqlite.connect(settings.sqlite_path) as db:
        for i, (page, space) in enumerate(all_pages):
            pid=page["id"]; title=page["title"]
            modified=page.get("version",{}).get("when","")
            url=f"{settings.confluence_url}/wiki/spaces/{space}/pages/{pid}"
            html=page.get("body",{}).get("storage",{}).get("value","")
            async with db.execute("SELECT last_modified FROM page_index WHERE page_id=?",(pid,)) as cur:
                row = await cur.fetchone()
            if row and row[0]==modified: _status["progress"]=i+1; continue
            text, links = parse_html(html, settings.confluence_url)
            chunks = split_text(text, settings.chunk_size_words, settings.chunk_overlap_words)
            if not chunks: continue
            vecs = await get_embeddings_batch(chunks)
            for chunk, vec in zip(chunks, vecs):
                points.append(models.PointStruct(id=str(uuid.uuid4()), vector=vec,
                    payload={"page_id":pid,"title":title,"space_key":space,
                             "space_name":page.get("space",{}).get("name",space),
                             "url":url,"content":chunk}))
            await db.execute("INSERT OR REPLACE INTO page_index (page_id,space_key,title,url,last_modified,indexed_at) VALUES (?,?,?,?,?,?)",
                (pid, space, title, url, modified, time.time()))
            for link in links:
                await db.execute("INSERT OR IGNORE INTO page_links (source_page_id,target_page_id) VALUES (?,?)",(pid,link))
            _status["progress"]=i+1
            if len(points)>=settings.upsert_batch_size: await upsert_points(points); points=[]
        await db.commit()
    if points: await upsert_points(points)
    await invalidate_cache()
    _status={"running":False,"progress":_status["total"],"total":_status["total"],"message":"Complete"}
