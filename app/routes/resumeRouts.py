from fastapi import APIRouter, HTTPException
from typing import List
from app.models.resume import Resume
from app.services.resumeService import (
    create_resume_service,
    get_all_resumes_service,
    get_resume_by_id_service,
    update_resume_service,
    delete_resume_service,
    analyze_resume_service,
)

router = APIRouter()


@router.post("/")
async def create_resume(resume: Resume):
    """
    Create a new resume.
    """
    resume_id = create_resume_service(resume)
    return {"message": "Resume created successfully.", "resume_id": resume_id}


@router.get("/", response_model=List[Resume])
async def get_all_resumes():
    """
    Retrieve all resumes.
    """
    return get_all_resumes_service()


@router.get("/{resume_id}", response_model=Resume)
async def get_resume_by_id(resume_id: str):
    """
    Retrieve a resume by its ID.
    """
    return get_resume_by_id_service(resume_id)


@router.put("/{resume_id}")
async def update_resume(resume_id: str, updated_resume: Resume):
    """
    Update a resume by its ID.
    """
    return update_resume_service(resume_id, updated_resume)


@router.delete("/{resume_id}")
async def delete_resume(resume_id: str):
    """
    Delete a resume by its ID.
    """
    return delete_resume_service(resume_id)


@router.post("/{resume_id}/analyze")
async def analyze_resume_by_id(resume_id: str, job_description: str):
    """
    Analyze a resume using ChatGPT.
    """
    return await analyze_resume_service(resume_id, job_description)
