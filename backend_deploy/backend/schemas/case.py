from pydantic import BaseModel, Field
from typing import Optional

class CaseRequest(BaseModel):
    query:         str   = Field(..., min_length=10, max_length=2000)
    case_type:     str   = Field(..., max_length=100)
    location:      str   = Field("India (General)", max_length=100)
    claim_amt:     float = Field(0, ge=0, le=1_000_000_000)
    language:      str   = Field("English", max_length=20)
    incident_date: Optional[str] = Field(None, max_length=20)

class CaseResponse(BaseModel):
    id:         Optional[str] = None
    query:      str
    analysis:   str
    win_prob:   int
    grade:      str
    laws:       str
    sources:    list
    landmarks:  list
    score_data: dict