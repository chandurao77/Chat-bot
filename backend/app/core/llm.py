import httpx, json
from typing import AsyncGenerator, List
from app.config import settings
async def stream_llm(messages: List[dict]) -> AsyncGenerator[str, None]:
    payload = {"model": settings.ollama_llm_model, "messages": messages, "stream": True,
        "options": {"temperature": settings.llm_temperature, "top_p": settings.llm_top_p,
                    "num_predict": settings.llm_num_predict}}
    async with httpx.AsyncClient(timeout=120) as client:
        async with client.stream("POST", f"{settings.ollama_base_url}/api/chat", json=payload) as resp:
            resp.raise_for_status()
            async for line in resp.aiter_lines():
                if not line.strip(): continue
                try:
                    token = json.loads(line).get("message",{}).get("content","")
                    if token: yield token
                except Exception: continue
