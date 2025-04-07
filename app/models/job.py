# app/models/job.py
from pydantic import BaseModel, HttpUrl, Field
from datetime import datetime
from typing import Optional, List


class Job(BaseModel):
    user_id: str
    job_title: str
    company_name: Optional[str] = None
    job_link: Optional[HttpUrl] = None
    job_description: str
    important_points: Optional[List[str]] = Field(default_factory=list)
    best_resume_id: Optional[str] = None
    created_at: datetime = datetime.utcnow()

    def dict(self, *args, **kwargs):
        d = super().dict(*args, **kwargs)
        if self.job_link:
            d["job_link"] = str(self.job_link)
        return d