# app/models/job.py
from pydantic import BaseModel, HttpUrl
from datetime import datetime
from typing import Optional


class Job(BaseModel):
    user_id: str  # Reference to the user who initiated the LinkedIn job search
    job_title: str  # Title of the job
    company_name: Optional[str] = None  # Optional company name
    job_link: Optional[HttpUrl] = None  # Link to the LinkedIn job post (optional)
    job_description: str  # Required job description
    best_resume_id: Optional[str] = None  # ID of the best matching resume
    created_at: datetime = datetime.utcnow()  # Timestamp when the job was saved

    def dict(self, *args, **kwargs):
        """Custom dict method to convert job_link to string if it exists."""
        d = super().dict(*args, **kwargs)
        if self.job_link:  # Check for None
            d["job_link"] = str(self.job_link)
        return d
