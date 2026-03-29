import time, uuid
import aiosqlite
from fastapi import APIRouter, Depends
from typing import Optional
from app.config import settings
from app.models.schemas import RenameRequest, FolderCreate
from app.api.dependencies import verify_api_key

router = APIRouter()

@router.get("/conversations", dependencies=[Depends(verify_api_key)])
async def list_conversations():
    async with aiosqlite.connect(settings.sqlite_path) as db:
        async with db.execute(
            "SELECT id,title,folder_id,created_at,updated_at FROM conversations ORDER BY updated_at DESC") as cur:
            rows = await cur.fetchall()
    return [{"id":r[0],"title":r[1],"folder_id":r[2],"created_at":r[3],"updated_at":r[4]} for r in rows]

@router.delete("/conversations/{conv_id}", dependencies=[Depends(verify_api_key)])
async def delete_conversation(conv_id: str):
    async with aiosqlite.connect(settings.sqlite_path) as db:
        await db.execute("DELETE FROM messages WHERE conversation_id=?", (conv_id,))
        await db.execute("DELETE FROM conversations WHERE id=?", (conv_id,))
        await db.commit()
    return {"status": "deleted"}

@router.patch("/conversations/{conv_id}", dependencies=[Depends(verify_api_key)])
async def rename_conversation(conv_id: str, body: RenameRequest):
    async with aiosqlite.connect(settings.sqlite_path) as db:
        await db.execute("UPDATE conversations SET title=? WHERE id=?", (body.title, conv_id))
        await db.commit()
    return {"status": "updated"}

@router.patch("/conversations/{conv_id}/move", dependencies=[Depends(verify_api_key)])
async def move_conversation(conv_id: str, folder_id: Optional[str] = None):
    async with aiosqlite.connect(settings.sqlite_path) as db:
        await db.execute("UPDATE conversations SET folder_id=? WHERE id=?", (folder_id, conv_id))
        await db.commit()
    return {"status": "moved"}

@router.post("/folders", dependencies=[Depends(verify_api_key)])
async def create_folder(body: FolderCreate):
    fid = str(uuid.uuid4())
    async with aiosqlite.connect(settings.sqlite_path) as db:
        await db.execute("INSERT INTO folders (id,name,created_at) VALUES (?,?,?)",
                         (fid, body.name, time.time()))
        await db.commit()
    return {"id": fid, "name": body.name}

@router.get("/folders", dependencies=[Depends(verify_api_key)])
async def list_folders():
    async with aiosqlite.connect(settings.sqlite_path) as db:
        async with db.execute("SELECT id,name,created_at FROM folders ORDER BY created_at") as cur:
            rows = await cur.fetchall()
    return [{"id": r[0], "name": r[1], "created_at": r[2]} for r in rows]

@router.delete("/folders/{folder_id}", dependencies=[Depends(verify_api_key)])
async def delete_folder(folder_id: str):
    async with aiosqlite.connect(settings.sqlite_path) as db:
        await db.execute("UPDATE conversations SET folder_id=NULL WHERE folder_id=?", (folder_id,))
        await db.execute("DELETE FROM folders WHERE id=?", (folder_id,))
        await db.commit()
    return {"status": "deleted"}

@router.patch("/folders/{folder_id}", dependencies=[Depends(verify_api_key)])
async def rename_folder(folder_id: str, body: RenameRequest):
    async with aiosqlite.connect(settings.sqlite_path) as db:
        await db.execute("UPDATE folders SET name=? WHERE id=?", (body.name, folder_id))
        await db.commit()
    return {"status": "updated"}
