import re
from typing import List

def split_by_heading(text: str, chunk_size: int = 256, overlap: int = 64) -> List[str]:
    sections = re.split(r"\n(?=#{1,6} )", text.strip())
    chunks = []
    for section in sections:
        lines = section.strip().split("\n")
        title = lines[0].lstrip("#").strip() if lines else ""
        body  = " ".join(lines[1:]).strip()
        words = body.split()
        for i in range(0, max(len(words), 1), chunk_size - overlap):
            window = words[i:i + chunk_size]
            if not window: continue
            prefix = f"{title}: " if title else ""
            chunks.append(prefix + " ".join(window))
    return chunks if chunks else [text[:1000]]
