from typing import AsyncGenerator, List
from app.config import settings
from app.services.embeddings import get_embedding
from app.services.vector_store import hybrid_search, search_by_page_ids
from app.services.semantic_cache import cache_lookup, cache_store
from app.services.content_guardrail import redact
from app.services.llm import stream_llm, SYSTEM_PROMPT
import aiosqlite

SMALL_TALK = {"hello","hi","hey","thanks","thank you","bye","goodbye","ok","okay","sure","yes","no","yep","nope"}

def _is_small_talk(text: str) -> bool:
    return text.lower().strip().rstrip("!?.") in SMALL_TALK

def _truncate(text: str, max_words: int) -> str:
    words = text.split()
    return " ".join(words[:max_words]) + ("..." if len(words) > max_words else "")

async def _graph_expand(seed_ids: List[str]) -> list:
    expanded = list(seed_ids)
    async with aiosqlite.connect(settings.sqlite_path) as db:
        for pid in seed_ids[:settings.graph_max_expansion]:
            async with db.execute(
                "SELECT target_page_id FROM page_links WHERE source_page_id=? LIMIT ?",
                (pid, settings.graph_max_expansion)) as cur:
                for (t,) in await cur.fetchall():
                    if t not in expanded:
                        expanded.append(t)
    new_ids = [p for p in expanded if p not in seed_ids]
    return await search_by_page_ids(new_ids) if new_ids else []

async def run_rag(question: str, history: List[dict]) -> AsyncGenerator[dict, None]:
    # Small talk bypass
    if _is_small_talk(question):
        responses = {"hello": "Hello! I'm JARVIS. Ask me anything about your documentation.",
                     "hi": "Hi there! How can I help you today?",
                     "hey": "Hey! What would you like to know?",
                     "thanks": "You're welcome! Let me know if you need anything else.",
                     "thank you": "Happy to help! Anything else?"}
        reply = responses.get(question.lower().strip().rstrip("!?."),
                              "I'm here to help! Ask me about your documentation.")
        yield {"type": "token", "data": reply}
        yield {"type": "sources", "data": []}
        yield {"type": "done", "data": ""}
        return

    # Semantic cache
    cached = await cache_lookup(question)
    if cached:
        yield {"type": "status", "data": "Found in cache..."}
        yield {"type": "token", "data": cached["answer"]}
        yield {"type": "sources", "data": cached.get("sources", [])}
        yield {"type": "done", "data": ""}
        return

    yield {"type": "status", "data": "Searching documents..."}

    # Hybrid search
    query_vec = await get_embedding(question, is_query=True)
    raw = await hybrid_search(query_vec, question, top_k=settings.retrieval_top_k,
                               score_threshold=settings.retrieval_score_threshold)

    # Graph RAG expansion
    seen = {}
    for r in raw:
        pid = r.payload.get("page_id", "")
        if pid not in seen: seen[pid] = r
    extra = await _graph_expand(list(seen.keys()))
    for r in extra:
        pid = r.payload.get("page_id", "")
        if pid not in seen and len(seen) < settings.llm_max_sources:
            seen[pid] = r

    sources_list = list(seen.values())[:settings.llm_max_sources]

    # Build context
    context_parts, citations = [], []
    for point in sources_list:
        p = point.payload or {}
        content = redact(_truncate(p.get("content", ""), 300))
        snippet = " ".join(content.split()[:30])
        title = p.get("title", "Unknown")
        context_parts.append(f"### {title}\n{content}")
        citations.append({
            "title": title, "space": p.get("space_key", ""),
            "score": round(getattr(point, "score", 0), 3),
            "url": p.get("url", ""), "snippet": snippet
        })

    context = "\n\n".join(context_parts) or "No relevant documentation found."

    yield {"type": "status", "data": "Generating answer..."}

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages += history[-(settings.max_history_turns * 2):]
    messages.append({"role": "user",
                     "content": f"Context:\n{context}\n\nQuestion: {question}"})

    full_answer = ""
    async for token in stream_llm(messages):
        full_answer += token
        yield {"type": "token", "data": token}

    yield {"type": "sources", "data": citations}
    yield {"type": "done", "data": ""}
    await cache_store(question, full_answer, citations)
