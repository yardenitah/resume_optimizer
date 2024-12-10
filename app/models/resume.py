from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime


class Resume(BaseModel):
    user_id: str  # Reference to the User who owns this resume
    title: str  # e.g., "Software Engineer Resume"
    content: str  # Raw resume content (or JSON structure for fields)
    job_descriptions: Optional[List[str]] = []  # Related job descriptions
    score: Optional[float] = None  # AI-generated score
    s3_url: Optional[str] = None  # URL of the uploaded file in S3
    created_at: datetime = datetime.utcnow()  # Automatically sets the current UTC time

