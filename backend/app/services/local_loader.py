import os, json, uuid
from app.config import settings
from app.utils.text_splitter import split_by_heading
from app.services.embeddings import get_embeddings_batch
from app.services.vector_store import ensure_collection, upsert_points
from app.services.semantic_cache import invalidate_cache
from qdrant_client import models

async def ingest_local() -> int:
    await ensure_collection()
    points = []
    path = settings.local_docs_path
    if not os.path.exists(path): return 0
    for fname in os.listdir(path):
        fpath = os.path.join(path, fname)
        if fname.endswith((".txt", ".md")):
            text = open(fpath, encoding="utf-8").read()
        elif fname.endswith(".json"):
            text = json.dumps(json.load(open(fpath)), indent=2)
        else: continue
        chunks = split_by_heading(text, settings.chunk_size, settings.chunk_overlap)
        vecs = await get_embeddings_batch(chunks)
        for chunk, vec in zip(chunks, vecs):
            points.append(models.PointStruct(id=str(uuid.uuid4()), vector=vec,
                payload={"page_id": f"local_{fname}_{uuid.uuid4().hex[:8]}",
                         "title": fname.replace("-", " ").replace("_", " ").rsplit(".", 1)[0].title(),
                         "space_key": "LOCAL", "space_name": "Local Documents",
                         "url": fpath, "content": chunk}))
    if points: await upsert_points(points)
    await invalidate_cache()
    return len(points)
