"""
backend/schemas/document.py
Pydantic schemas for Document Vault.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class DocumentMetadata(BaseModel):
    doc_type:    str            = "Other"
    parties:     list[str]      = []
    key_dates:   list[str]      = []
    case_number: Optional[str]  = None
    court:       Optional[str]  = None
    summary:     str            = ""
    tags:        list[str]      = []


class DocumentOut(BaseModel):
    id:           str
    filename:     str
    label:        str
    size_bytes:   int
    created_at:   Optional[datetime] = None
    metadata:     DocumentMetadata


class DocumentSearchRequest(BaseModel):
    query: str = Field(..., min_length=2, max_length=200)