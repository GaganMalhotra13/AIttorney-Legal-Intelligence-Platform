from pydantic import BaseModel,Field
from typing import Optional


class OpponentRequest(BaseModel):
    query:        str = Field(..., min_length=5, max_length=2000)
    live_context: str = Field("", max_length=10000)  # ← cap context size

class EvidenceRequest(BaseModel):
    query:     str = Field(..., min_length=5, max_length=2000)
    case_type: str = Field(..., max_length=100)

class SettlementRequest(BaseModel):
    query:        str   = Field(..., min_length=5, max_length=2000)
    claim_amount: float = Field(..., ge=0, le=1_000_000_000)
    case_type:    str   = Field(..., max_length=100)
    live_context: str   = Field("", max_length=10000)

class BriefRequest(BaseModel):
    query:        str = Field(..., min_length=5, max_length=2000)
    live_context: str = Field("", max_length=10000)
    score_data:   dict = Field(default_factory=dict)
    laws_text:    str = Field("", max_length=2000)
    party_name:   str = Field("Complainant", max_length=100)

class JurisdictionRequest(BaseModel):
    query:    str
    location: str = "India"

class TimelineRequest(BaseModel):
    query:      str
    score_data: dict
    case_type:  str


class FIRRequest(BaseModel):
    query:        str
    complainant:  str = ""
    accused_desc: str = ""
    location:     str = "India"

class MediationRequest(BaseModel):
    query:         str
    your_position: str = ""
    other_party:   str = ""
    ideal_outcome: str = ""

class LimitationRequest(BaseModel):
    case_type:     str
    incident_date: str
    query:         str

class ComparatorRequest(BaseModel):
    query:        str
    live_context: str
    case_type:    str