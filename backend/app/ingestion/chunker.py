import re
from typing import List


def split_text(text: str, chunk_size: int = 512, overlap: int = 64) -> List[str]:
    """Split text into chunks of at most `chunk_size` words.

    Sentences are kept together where possible. A sentence longer than
    `chunk_size` (or text with no punctuation at all) is split by words.
    Consecutive chunks share up to `overlap` trailing words.
    """
    if chunk_size < 1:
        raise ValueError("chunk_size must be >= 1")
    overlap = max(0, min(overlap, chunk_size - 1))

    # Break into sentences, then into word lists no longer than chunk_size.
    units: List[List[str]] = []
    for sentence in re.split(r'(?<=[.!?])\s+', text.strip()):
        words = sentence.split()
        for i in range(0, len(words), chunk_size):
            units.append(words[i:i + chunk_size])

    chunks: List[str] = []
    current: List[str] = []
    fresh = 0  # words in `current` not yet emitted in a chunk
    for words in units:
        if current and len(current) + len(words) > chunk_size:
            chunks.append(" ".join(current))
            current = current[-overlap:] if overlap else []
            fresh = 0
            # The carried overlap must still leave room for the next unit.
            if len(current) + len(words) > chunk_size:
                current = current[len(current) + len(words) - chunk_size:]
        current.extend(words)
        fresh += len(words)
    if current and fresh:
        chunks.append(" ".join(current))
    return chunks
