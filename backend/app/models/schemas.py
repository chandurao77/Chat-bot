from pydantic import BaseModel, Field
from typing import Optional, List

class ChatRequest(BaseModel):
    question: str = Field(..., max_length=2000)
    conversation_id: Optional[str] = None

class SourceCitation(BaseModel):
    title: str
    space: str
    score: float
    url: str
    snippet: str = ""

class FeedbackRequest(BaseModel):
    conversation_id: str
    message_id: str
    vote: int
    question: Optional[str] = None
    answer: Optional[str] = None

class RenameRequest(BaseModel):
    title: str

class FolderCreate(BaseModel):
    name: str

class IngestRequest(BaseModel):
    spaces: Optional[List[str]] = None
