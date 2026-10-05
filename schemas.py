from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


class DocumentRequest(BaseModel):
    document_type: Literal[
        "Non-Disclosure Agreement", "Freelance Service Agreement",
        "Residential Lease Agreement", "Employment Agreement", "Custom Agreement",
    ]
    first_party: str = Field(min_length=2, max_length=160)
    second_party: str = Field(min_length=2, max_length=160)
    effective_date: date
    jurisdiction: str = Field(default="India", min_length=2, max_length=100)
    terms: str = Field(min_length=5, max_length=5000)
    language: Literal["English", "Tamil"] = "English"


class ExportRequest(BaseModel):
    title: str = Field(default="Legal document", max_length=160)
    content: str = Field(min_length=1, max_length=30000)
