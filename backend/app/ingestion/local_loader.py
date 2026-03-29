import os, json, uuid
from app.config import settings
from app.ingestion.chunker import split_text
from app.core.embeddings import get_embeddings_batch
from app.core.vector_store import ensure_collection, upsert_points
from app.core.semantic_cache import invalidate_cache
from qdrant_client import models
async def ingest_local() -> int:
    await ensure_collection()
    points = []
    for fname in os.listdir(settings.local_docs_path):
        fpath = os.path.join(settings.local_docs_path, fname)
        if fname.endswith((".txt",".md")):
            text = open(fpath, encoding="utf-8").read()
        elif fname.endswith(".json"):
            text = json.dumps(json.load(open(fpath)), indent=2)
        else: continue
        chunks = split_text(text, settings.chunk_size_words, settings.chunk_overlap_words)
        vecs   = await get_embeddings_batch(chunks)
        for chunk, vec in zip(chunks, vecs):
            points.append(models.PointStruct(id=str(uuid.uuid4()), vector=vec,
                payload={"page_id":f"local_{fname}_{uuid.uuid4().hex[:8]}","title":fname,
                         "space_key":"LOCAL","space_name":"Local Documents","url":fpath,"content":chunk}))
    if points: await upsert_points(points)
    await invalidate_cache()
    return len(points)
