# app/services/jobService.py
import time
from typing import Optional
import asyncio
from app.database.connection import MongoDBConnection
from app.models.job import Job
from bson import ObjectId
from fastapi import HTTPException
from datetime import datetime
from app.utils.chatgpt_service import extract_important_points_from_job
from app.services.resumeService import find_best_resume_service
from app.utils import LinkedInManager

# Initialize MongoDB connection
db_connection = MongoDBConnection()
db = db_connection.get_database()
jobs_collection = db["jobs"]  # New collection for jobs


def search_and_save_linkedin_jobs_service(
    user_id, username, password, experience_level, job_titles, maxNumberOfJobsTosearch
):
    linkedin_manager = LinkedInManager.LinkedInManager(username, password, experience_level)

    if not linkedin_manager.login():
        raise Exception("Failed to login to LinkedIn.")

    job_results = linkedin_manager.search_jobs_for_titles(job_titles, maxNumberOfJobsTosearch)
    saved_jobs = []

    for job in job_results:
        company_name, job_description, job_title, job_link = job

        # Run async logic in sync context
        best_resume_result = asyncio.run(find_best_resume_service(user_id, job_description, job_title))
        best_resume_id = best_resume_result["best_resume"]["id"]

        saved_job = asyncio.run(save_job_service(
            user_id=user_id,
            job_title=job_title,
            job_link=job_link,
            company_name=company_name,
            job_description=job_description,
            best_resume_id=best_resume_id,
        ))

        saved_jobs.append(saved_job)

    linkedin_manager.logout()


async def save_job_service(user_id: str, job_title: str, job_link: str, company_name: str, job_description: str, best_resume_id: str):
    """ Save a new job with the best matching resume ID. """
    important_points = await extract_important_points_from_job(job_title, job_description)

    job_data = Job(
        user_id=user_id,
        job_title=job_title,
        company_name=company_name,
        job_link=job_link,
        job_description=job_description,
        best_resume_id=best_resume_id,
        important_points=important_points,
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


def delete_user_jobs_service(user_id: str):
    """Delete all jobs for a specific user."""
    result = jobs_collection.delete_many({"user_id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="No jobs found to delete.")
    return {"message": f"Deleted {result.deleted_count} jobs successfully."}


def delete_job_by_id_service(user_id: str, job_id: str):
    """
    Delete a specific job by its ID for a given user.
    """
    result = jobs_collection.delete_one({"_id": ObjectId(job_id), "user_id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Job not found or not authorized to delete.")
    return {"message": "Job deleted successfully."}


def search_jobs_by_title_service(user_id: str, title: str):
    """
    Search for jobs by title for a specific user.
    """
    # Use case-insensitive regex to match job titles containing the search term
    jobs = list(
        jobs_collection.find(
            {
                "user_id": user_id,
                "job_title": {"$regex": title, "$options": "i"},
            }
        )
    )
    if not jobs:
        raise HTTPException(status_code=404, detail="No jobs found with the given title.")

    for job in jobs:
        job["_id"] = str(job["_id"])  # Convert ObjectId to string for JSON serialization
    return jobs


def get_job_important_points_service(user_id: str, job_id: str) -> list[str]:
    job = jobs_collection.find_one({"_id": ObjectId(job_id), "user_id": user_id})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found or not authorized to view.")

    return job.get("important_points", [])


def get_job_important_points_service(user_id: str, job_id: str) -> list[str]:
    job = jobs_collection.find_one({"_id": ObjectId(job_id), "user_id": user_id})
    if not job:
        raise HTTPException(status_code=404, detail="Job not found or not authorized to view.")

    return job.get("important_points", [])