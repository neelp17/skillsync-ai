from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field


class AnalysisUpdate(BaseModel):
    role: str | None = Field(default=None, min_length=1, max_length=200)
    skills: str | None = Field(default=None, min_length=1, max_length=5000)


class AnalysisRecord(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    role: str
    skills: str
    analysis: str
    source: str
    created_at: datetime
    updated_at: datetime
