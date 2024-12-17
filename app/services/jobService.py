# app/services/jobService.py
from app.database.connection import MongoDBConnection
from app.models.job import Job
from bson import ObjectId
from fastapi import HTTPException
from datetime import datetime

# Initialize MongoDB connection
db_connection = MongoDBConnection()
db = db_connection.get_database()
jobs_collection = db["jobs"]  # New collection for jobs


def save_job_service(user_id: str, job_title: str, job_link: str, company_name: str, job_description: str, best_resume_id: str):
    """
    Save a new job with the best matching resume ID.
    """
    job_data = Job(
        user_id=user_id,
        job_title=job_title,
        company_name=company_name,
        job_link=job_link,
        job_description=job_description,
        best_resume_id=best_resume_id,
        created_at=datetime.utcnow()
    )
    result = jobs_collection.insert_one(job_data.dict())
    if not result.inserted_id:
        raise HTTPException(status_code=500, detail="Failed to save the job details.")
    return {"message": "Job saved successfully.", "job_id": str(result.inserted_id)}


def get_user_jobs_service(user_id: str):
    """
    Retrieve all saved jobs for a specific user.
    """
    jobs = list(jobs_collection.find({"user_id": user_id}))
    for job in jobs:
        job["_id"] = str(job["_id"])  # Convert ObjectId to string for JSON serialization
    return jobs
