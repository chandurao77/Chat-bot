\
import re
from typing import List
def split_text(text: str, chunk_size: int=512, overlap: int=64) -> List[str]:
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    chunks, current, cur_len = [], [], 0
    for sentence in sentences:
        words = sentence.split()
        if cur_len + len(words) > chunk_size and current:
            chunks.append(" ".join(current))
            tail = current[-overlap:] if len(current) > overlap else current[:]
            current = tail + words; cur_len = len(current)
        else:
            current.extend(words); cur_len += len(words)
    if current: chunks.append(" ".join(current))
    return chunks
