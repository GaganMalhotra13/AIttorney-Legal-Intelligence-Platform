from pydantic import BaseModel
from typing import Optional

class CaseRequest(BaseModel):
    query:         str
    case_type:     str
    location:      str   = "India (General)"
    claim_amt:     float = 0
    language:      str   = "English"
    incident_date: Optional[str] = None

class CaseResponse(BaseModel):
    query:      str
    analysis:   str
    win_prob:   int
    grade:      str
    laws:       str
    sources:    list
    score_data: dict