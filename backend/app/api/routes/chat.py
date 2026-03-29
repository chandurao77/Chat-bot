import json, uuid
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
from slowapi import Limiter
from slowapi.util import get_remote_address
from app.config import settings
from app.models.schemas import ChatRequest
from app.services.rag import run_rag
from app.services.input_guardrail import check_input
from app.services.conversation_store import get_history, save_turn

router = APIRouter()
limiter = Limiter(key_func=get_remote_address)

@router.post("/chat/stream")
@limiter.limit(f"{settings.rate_limit_rpm}/minute")
async def chat_stream(request: Request, body: ChatRequest):
    question = body.question.strip()
    conv_id = body.conversation_id or str(uuid.uuid4())

    # Input guardrail
    ok, msg = check_input(question)
    if not ok:
        async def blocked():
            yield f"event: error\ndata: {json.dumps({'message': msg})}\n\n"
            yield "event: done\ndata: {}\n\n"
        return StreamingResponse(blocked(), media_type="text/event-stream",
                                 headers={"X-Conversation-Id": conv_id})

    history = await get_history(conv_id)

    async def event_stream():
        full_answer, sources = "", []
        async for event in run_rag(question, history):
            if event["type"] == "status":
                yield f"event: status\ndata: {json.dumps({'message': event['data']})}\n\n"
            elif event["type"] == "token":
                full_answer += event["data"]
                yield f"event: token\ndata: {json.dumps({'text': event['data']})}\n\n"
            elif event["type"] == "sources":
                sources = event["data"]
                yield f"event: sources\ndata: {json.dumps(sources)}\n\n"
            elif event["type"] == "done":
                yield "event: done\ndata: {}\n\n"
        await save_turn(conv_id, question, full_answer)

    return StreamingResponse(event_stream(), media_type="text/event-stream",
                             headers={"X-Conversation-Id": conv_id})
