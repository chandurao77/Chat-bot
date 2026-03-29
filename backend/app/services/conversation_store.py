import time, uuid
import aiosqlite
from app.config import settings

async def get_history(conversation_id: str) -> list:
    async with aiosqlite.connect(settings.sqlite_path) as db:
        async with db.execute(
            "SELECT role, content FROM messages WHERE conversation_id=? ORDER BY created_at DESC LIMIT ?",
            (conversation_id, settings.max_history_turns * 2)) as cur:
            rows = await cur.fetchall()
    return [{"role": r, "content": c} for r, c in reversed(rows)]

async def save_turn(conversation_id: str, question: str, answer: str):
    now = time.time()
    async with aiosqlite.connect(settings.sqlite_path) as db:
        await db.execute(
            "INSERT OR IGNORE INTO conversations (id,title,created_at,updated_at) VALUES (?,?,?,?)",
            (conversation_id, question[:60], now, now))
        await db.execute("UPDATE conversations SET updated_at=? WHERE id=?", (now, conversation_id))
        for role, content in [("user", question), ("assistant", answer)]:
            await db.execute(
                "INSERT INTO messages (id,conversation_id,role,content,created_at) VALUES (?,?,?,?,?)",
                (str(uuid.uuid4()), conversation_id, role, content[:4000], now))
        await db.commit()
