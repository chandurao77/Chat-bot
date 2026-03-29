import aiosqlite
from app.config import settings

async def init_db():
    async with aiosqlite.connect(settings.sqlite_path) as db:
        await db.execute("PRAGMA journal_mode=WAL")
        await db.execute("""CREATE TABLE IF NOT EXISTS conversations (
            id TEXT PRIMARY KEY, title TEXT, folder_id TEXT,
            created_at REAL, updated_at REAL)""")
        await db.execute("""CREATE TABLE IF NOT EXISTS messages (
            id TEXT PRIMARY KEY, conversation_id TEXT, role TEXT,
            content TEXT, created_at REAL,
            FOREIGN KEY(conversation_id) REFERENCES conversations(id))""")
        await db.execute("""CREATE TABLE IF NOT EXISTS feedback (
            id TEXT PRIMARY KEY, conversation_id TEXT, message_id TEXT,
            vote INTEGER, created_at REAL)""")
        await db.execute("""CREATE TABLE IF NOT EXISTS page_index (
            page_id TEXT PRIMARY KEY, space_key TEXT, title TEXT,
            url TEXT, last_modified TEXT, indexed_at REAL)""")
        await db.execute("""CREATE TABLE IF NOT EXISTS page_links (
            source_page_id TEXT, target_page_id TEXT,
            PRIMARY KEY (source_page_id, target_page_id))""")
        await db.execute("""CREATE TABLE IF NOT EXISTS folders (
            id TEXT PRIMARY KEY, name TEXT, created_at REAL)""")
        await db.commit()
