from fastapi import APIRouter, Depends, BackgroundTasks
from pydantic import BaseModel
from typing import List, Optional
from app.api.deps import verify_api_key
from app.ingestion.confluence_loader import ingest_confluence, get_status
from app.ingestion.local_loader import ingest_local
router = APIRouter()
class IngestRequest(BaseModel):
    spaces: Optional[List[str]] = None
@router.post("/ingest", status_code=202, dependencies=[Depends(verify_api_key)])
async def start_ingestion(body: IngestRequest, bg: BackgroundTasks):
    bg.add_task(ingest_confluence, body.spaces)
    return {"status":"ingestion started"}
@router.post("/ingest/local", status_code=202, dependencies=[Depends(verify_api_key)])
async def start_local_ingestion(bg: BackgroundTasks):
    bg.add_task(ingest_local)
    return {"status":"local ingestion started"}
@router.get("/ingest/status")
async def ingest_status():
    return get_status()
