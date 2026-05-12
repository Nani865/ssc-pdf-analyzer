"""Pydantic schemas for request/response validation"""
from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List

# Paper Schemas
class PaperBase(BaseModel):
    original_filename: str
    exam_year: Optional[str] = None
    exam_name: Optional[str] = None

class PaperCreate(PaperBase):
    pass

class PaperResponse(PaperBase):
    id: int
    filename: str
    total_pages: int
    uploaded_at: datetime
    processed: bool
    error_message: Optional[str] = None

    class Config:
        from_attributes = True

class PaperDetailResponse(PaperResponse):
    questions: List['QuestionResponse'] = []

# Question Schemas
class QuestionBase(BaseModel):
    text: str
    page_number: int
    question_number: Optional[int] = None
    topic: Optional[str] = None
    difficulty: Optional[str] = None

class QuestionCreate(QuestionBase):
    paper_id: int

class QuestionResponse(QuestionBase):
    id: int
    paper_id: int
    extracted_at: datetime
    hash_value: str

    class Config:
        from_attributes = True

# Similarity Schemas
class SimilarityResponse(BaseModel):
    id: int
    question_id_1: int
    question_id_2: int
    similarity_score: float = Field(..., ge=0, le=1)
    similarity_type: str
    detected_at: datetime

    class Config:
        from_attributes = True

# Analytics Schemas
class AnalyticsQuestion(BaseModel):
    question_id: int
    text: str
    paper_ids: List[int]
    occurrences: int
    similarity_score: float

class AnalyticsSummary(BaseModel):
    total_papers: int
    total_questions: int
    unique_questions: int
    repeated_questions: int
    top_repeated: List[AnalyticsQuestion]
    by_topic: dict
    by_difficulty: dict

class ExportResponse(BaseModel):
    status: str
    message: str
    download_url: str
    format: str

class UploadResponse(BaseModel):
    status: str
    message: str
    uploaded_files: List[str]
    failed_files: Optional[List[dict]] = None
