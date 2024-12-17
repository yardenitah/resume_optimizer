# app/routes/jobRoutes.py
from fastapi import APIRouter, HTTPException, Depends, Form, Query
from app.services.jobService import save_job_service, get_user_jobs_service
from app.services.resumeService import find_best_resume_service
from app.utils.jwt import verify_token

router = APIRouter()


@router.post("/save", status_code=201)
async def save_job(
        job_title: str = Form(..., description="Title of the job"),
        company_name: str = Form(None, description="Company name"),
        job_link: str = Form(None, description="Optional job link"),
        job_description: str = Form(..., description="Required job description"),
        token: dict = Depends(verify_token)
):
    """
    Save a job along with the best matching resume.
    """
    user_id = token.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized.")

    # Find the best matching resume for the job
    best_resume_result = await find_best_resume_service(user_id, job_description, job_title)
    best_resume_id = best_resume_result["best_resume"]["id"]

    # Save job details to MongoDB
    result = save_job_service(
        user_id=user_id,
        job_title=job_title,
        job_link=job_link,
        company_name=company_name,
        job_description=job_description,
        best_resume_id=best_resume_id
    )
    return result


@router.get("/", status_code=200)
async def get_user_jobs(token: dict = Depends(verify_token)):
    """
    Retrieve all saved jobs for the authenticated user.
    """
    user_id = token.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized.")

    jobs = get_user_jobs_service(user_id)
    return jobs
