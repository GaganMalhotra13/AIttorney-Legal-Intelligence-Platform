from pydantic import BaseModel, Field
from typing import Optional

class AuditRequest(BaseModel):
    text: str = Field(..., min_length=50, max_length=15000)
    role: str = Field(..., max_length=50)
class ChatRequest(BaseModel):
    question: str
    context:  str
    doc_id:   Optional[str] = None