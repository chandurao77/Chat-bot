import aiosqlite
from typing import List
from app.config import settings
from app.core.vector_store import search_by_page_ids
async def expand_context(seed_page_ids: List[str]) -> list:
    expanded = list(seed_page_ids)
    async with aiosqlite.connect(settings.sqlite_path) as db:
        for pid in seed_page_ids[:settings.graph_rag_max_extra]:
            async with db.execute(
                "SELECT target_page_id FROM page_links WHERE source_page_id=? LIMIT ?",
                (pid, settings.graph_rag_max_extra)) as cur:
                for (t,) in await cur.fetchall():
                    if t not in expanded:
                        expanded.append(t)
                        if len(expanded) >= len(seed_page_ids)+settings.graph_rag_max_extra: break
    new_ids = [p for p in expanded if p not in seed_page_ids]
    return await search_by_page_ids(new_ids) if new_ids else []
