import json, uuid, time
import aiosqlite
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.config import settings
from app.core.rag_pipeline import run_rag
from app.core.spell_check import correct_query
router = APIRouter()
limiter = Limiter(key_func=get_remote_address)
class ChatRequest(BaseModel):
    question: str = Field(..., max_length=2000)
    conversation_id: str | None = None
@router.post("/chat/stream")
@limiter.limit(f"{settings.rate_limit_rpm}/minute")
async def chat_stream(request: Request, body: ChatRequest):
    question, was_corrected = correct_query(body.question.strip())
    conv_id = body.conversation_id or str(uuid.uuid4())
    history = []
    async with aiosqlite.connect(settings.sqlite_path) as db:
        async with db.execute(
            "SELECT role,content FROM messages WHERE conversation_id=? ORDER BY created_at DESC LIMIT ?",
            (conv_id, settings.conversation_history_turns*2)) as cur:
            history = [{"role":r,"content":c} for r,c in reversed(await cur.fetchall())]
    async def event_stream():
        if was_corrected:
            yield f"event: query_corrected\ndata: {json.dumps({'original':body.question,'corrected':question})}\n\n"
        full_answer, sources = "", []
        async for event in run_rag(question, history, conv_id):
            if event["type"]=="token":
                full_answer += event["data"]
                yield f"event: token\ndata: {json.dumps({'text':event['data']})}\n\n"
            elif event["type"]=="sources":
                sources = event["data"]
                yield f"event: sources\ndata: {json.dumps(sources)}\n\n"
            elif event["type"]=="done":
                yield "event: done\ndata: {}\n\n"
        now = time.time()
        async with aiosqlite.connect(settings.sqlite_path) as db:
            await db.execute("INSERT OR IGNORE INTO conversations (id,title,created_at,updated_at) VALUES (?,?,?,?)",
                (conv_id, question[:60], now, now))
            await db.execute("UPDATE conversations SET updated_at=? WHERE id=?", (now, conv_id))
            for role, content in [("user",question),("assistant",full_answer)]:
                await db.execute("INSERT INTO messages (id,conversation_id,role,content,created_at) VALUES (?,?,?,?,?)",
                    (str(uuid.uuid4()), conv_id, role, content[:2000], now))
            await db.commit()
    return StreamingResponse(event_stream(), media_type="text/event-stream",
                             headers={"X-Conversation-Id": conv_id})
