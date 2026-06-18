from pydantic import BaseModel
from typing import Optional

class AuditRequest(BaseModel):
    text: str
    role: str

class ChatRequest(BaseModel):
    question: str
    context:  str
    doc_id:   Optional[str] = None