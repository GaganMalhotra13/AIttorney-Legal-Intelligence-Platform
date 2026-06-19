# backend/schemas/user.py
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class UserRegister(BaseModel):
    email:    EmailStr
    password: str
    name:     str

class UserLogin(BaseModel):
    email:    EmailStr
    password: str

class UserOut(BaseModel):
    id:         str
    email:      str
    name:       str
    created_at: datetime


# backend/schemas/case.py
class CaseRequest(BaseModel):
    query:      str
    case_type:  str
    location:   str  = "India (General)"
    claim_amt:  float = 0
    language:   str  = "English"
    incident_date: Optional[str] = None

class CaseResponse(BaseModel):
    query:       str
    analysis:    str
    win_prob:    int
    grade:       str
    laws:        str
    sources:     list[dict]
    score_data:  dict


# backend/schemas/contract.py
class AuditRequest(BaseModel):
    text: str
    role: str

class ChatRequest(BaseModel):
    question: str
    context:  str
    doc_id:   Optional[str] = None


# backend/schemas/notice.py
class NoticeRequest(BaseModel):
    context:   str
    sender:    str = ""
    recipient: str = ""
    tone:      str = "Professional"


# backend/schemas/brain.py
class OpponentRequest(BaseModel):
    query:       str
    live_context:str

class EvidenceRequest(BaseModel):
    query:     str
    case_type: str

class SettlementRequest(BaseModel):
    query:        str
    claim_amount: float
    case_type:    str
    live_context: str

class JurisdictionRequest(BaseModel):
    query:    str
    location: str = "India"

class TimelineRequest(BaseModel):
    query:      str
    score_data: dict
    case_type:  str

class BriefRequest(BaseModel):
    query:        str
    live_context: str
    score_data:   dict
    laws_text:    str
    party_name:   str = "Complainant"

class FIRRequest(BaseModel):
    query:          str
    complainant:    str = ""
    accused_desc:   str = ""
    location:       str = "India"

class MediationRequest(BaseModel):
    query:        str
    your_position:str = ""
    other_party:  str = ""
    ideal_outcome:str = ""

class LimitationRequest(BaseModel):
    case_type:     str
    incident_date: str
    query:         str

class ComparatorRequest(BaseModel):
    query:        str
    live_context: str
    case_type:    str