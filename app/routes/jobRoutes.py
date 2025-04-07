# app/routes/jobRoutes.py
from fastapi import (
    APIRouter,
    HTTPException,
    Depends,
    Form,
    Query,
    BackgroundTasks
)
from app.services.jobService import (
    save_job_service,
    get_user_jobs_service,
    search_and_save_linkedin_jobs_service,
    delete_user_jobs_service,
    delete_job_by_id_service,
    search_jobs_by_title_service, get_job_important_points_service,
)
from app.services.resumeService import find_best_resume_service
from app.utils.jwt import verify_token
import asyncio
from fastapi.concurrency import run_in_threadpool

router = APIRouter()


@router.post("/linkedin/search", status_code=200)
async def search_and_save_jobs_in_linkedin(
    linkedin_username: str = Form(...),
    linkedin_password: str = Form(...),
    experience_level: str = Form(...),
    job_titles: list[str] = Form(...),
    maxNumberOfJobsTosearch: int = Form(100),
    token: dict = Depends(verify_token),
):
    user_id = token.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized.")

    if maxNumberOfJobsTosearch > 25 or maxNumberOfJobsTosearch < 0:
        raise HTTPException(status_code=400, detail="Invalid max number of jobs.")

    experience_level = experience_level.lower()
    valid_levels = {'no filter', 'entry level', 'mid-senior'}
    if experience_level not in valid_levels:
        raise HTTPException(status_code=400, detail=f"Invalid experience level: {experience_level}")

    await run_in_threadpool(
        search_and_save_linkedin_jobs_service,
        user_id,
        linkedin_username,
        linkedin_password,
        experience_level,
        job_titles,
        maxNumberOfJobsTosearch,
    )

    return {"message": "LinkedIn job scraping completed."}



@router.post("/save", status_code=201)
async def save_job(job_title: str = Form(..., description="Title of the job"),company_name: str = Form(None, description="Company name"),job_link: str = Form(None, description="Optional job link"),job_description: str = Form(..., description="Required job description"),token: dict = Depends(verify_token)):
    """Save a job along with the best matching resume."""
    user_id = token.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized.")

    best_resume_result = await find_best_resume_service(user_id, job_description, job_title)
    best_resume_id = best_resume_result["best_resume"]["id"]
    print(f"\nbest_resume_id: {best_resume_id}\n\n")

    result = await save_job_service(
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

@router.delete("/delete", status_code=200)
async def delete_user_jobs(token: dict = Depends(verify_token)):
    """
    Delete all saved jobs for the authenticated user.
    """
    user_id = token.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized.")

    result = delete_user_jobs_service(user_id)
    return result


@router.delete("/delete/{job_id}", status_code=200)
async def delete_job_by_id(job_id: str, token: dict = Depends(verify_token)):
    """
    Delete a specific job by its ID.
    """
    user_id = token.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized.")

    result = delete_job_by_id_service(user_id, job_id)
    return result

@router.get("/search", status_code=200)
async def search_jobs_by_title(title: str = Query(..., description="Title of the job to search for"), token: dict = Depends(verify_token),):
    """
    Search for jobs by title for the authenticated user.
    """
    user_id = token.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized.")

    jobs = search_jobs_by_title_service(user_id, title)
    return jobs



@router.get("/jobpoint/{job_id}", status_code=200)
async def get_jobpoint(job_id: str, token: dict = Depends(verify_token)):
    """
    Get the important points to remember for a specific job.
    """
    user_id = token.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Unauthorized.")

    points = get_job_important_points_service(user_id, job_id)
    return {"job_id": job_id, "important_points": points}