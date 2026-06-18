from pydantic import BaseModel
from typing import Optional

class OpponentRequest(BaseModel):
    query:        str
    live_context: str

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