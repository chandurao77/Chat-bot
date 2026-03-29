import uuid, time, hashlib
import aiosqlite
from fastapi import APIRouter, Depends
from app.config import settings
from app.models.schemas import FeedbackRequest
from app.services.embeddings import get_embedding
from app.api.dependencies import verify_api_key
from qdrant_client import AsyncQdrantClient, models

router = APIRouter()

@router.post("/feedback", dependencies=[Depends(verify_api_key)])
async def submit_feedback(body: FeedbackRequest):
    fid = str(uuid.uuid4())
    async with aiosqlite.connect(settings.sqlite_path) as db:
        await db.execute(
            "INSERT INTO feedback (id,conversation_id,message_id,vote,created_at) VALUES (?,?,?,?,?)",
            (fid, body.conversation_id, body.message_id, body.vote, time.time()))
        await db.commit()
    if body.vote == 1 and body.question and body.answer:
        combined = f"Q: {body.question}\nA: {body.answer}"
        hex_id = hashlib.md5(combined.encode()).hexdigest()
        numeric_id = int(hex_id, 16) % (2 ** 63)
        vec = await get_embedding(combined)
        client = AsyncQdrantClient(url=settings.qdrant_url)
        await client.upsert(collection_name=settings.qdrant_collection,
            points=[models.PointStruct(id=numeric_id, vector=vec,
                payload={"page_id": f"learned_{hex_id}", "title": body.question[:80],
                         "content": combined, "space_key": "LEARNED",
                         "space_name": "Verified Answers", "url": ""})])
        await client.close()
    return {"status": "ok", "id": fid}
