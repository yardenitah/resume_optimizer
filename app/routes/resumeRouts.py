# app/routes/resumeRouts.py
from fastapi import APIRouter, Depends, HTTPException, Header
from typing import List
from app.utils.jwt import verify_token
from app.models.resume import Resume
from app.services.resumeService import (
    create_resume_service,
    get_all_resumes_service,
    get_resume_by_id_service,
    update_resume_service,
    delete_resume_service,
    analyze_resume_service,
)
from app.utils.admin_verification import verify_admin  # Import the verify_admin dependency

router = APIRouter()


@router.post("/")
async def upload_resume(resume: Resume, Authorization: str = Header(None)):
    """
    Upload a new resume for the user.
    """
    # Validate the user's token
    user_payload = verify_token(Authorization)
    print(f"user_payload: {user_payload}")
    user_id = user_payload.get("sub")
    print(f'user_id: {user_id}')

    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid user token.")

    # Add the user ID to the resume object
    resume.user_id = user_id

    # Save the resume using the service
    resume_id = await create_resume_service(resume)
    return {"message": "Resume uploaded successfully.", "resume_id": resume_id}


@router.get("/", response_model=List[Resume], dependencies=[Depends(verify_admin)])  # Enforce admin access
async def get_all_resumes():
    pass


@router.get("/{resume_id}", response_model=Resume)
async def get_resume_by_id(resume_id: str):
    pass


@router.put("/{resume_id}")
async def update_resume_list(resume_id: str, updated_resume: Resume):
    pass


@router.delete("/{resume_id}")
async def delete_resume_from_resumeList(resume_id: str):
    pass


@router.post("/{resume_id}/analyze")
async def analyze_resume_by_id(resume_id: str, job_description: str):
    """
    Analyze a resume using ChatGPT.
    """
    return await analyze_resume_service(resume_id, job_description)
