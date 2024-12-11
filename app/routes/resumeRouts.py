# app/routes/resumeRouts.py
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Depends, Query
from app.services.resumeService import upload_resume_service, get_resumes_service, get_presigned_url_service, \
    delete_all_resumes_service, delete_user_resume_service
from app.utils.jwt import verify_token

router = APIRouter()


@router.post("/upload", status_code=201)
async def upload_resume(
        token: dict = Depends(verify_token),
        file: UploadFile = File(...),
        title: str = Form(...),
):
    """
    Upload a resume file.
    """
    user_id = token.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid user.")

    # Validate file type
    allowed_extensions = ["pdf", "docx"]
    file_extension = file.filename.split(".")[-1].lower()
    if file_extension not in allowed_extensions:
        raise HTTPException(status_code=400, detail="Unsupported file type.")

    res = upload_resume_service(user_id, file.file, title, file_extension)
    return res


@router.get("/{resume_id}/download", status_code=200)
async def get_presigned_url(
        resume_id: str,
        expiration: int = Query(3600, ge=60, le=86400),
        token: dict = Depends(verify_token),
):
    """
    Get a pre-signed URL to download or view a specific resume.
    """
    user_id = token.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid user.")

    presigned_url = get_presigned_url_service(user_id, resume_id, expiration)
    return {"presigned_url": presigned_url}


@router.get("/", status_code=200)
async def get_user_resumes(
        token: dict = Depends(verify_token),
        skip: int = Query(0, ge=0),
        limit: int = Query(10, ge=1),
):
    """
    Get all resumes uploaded by the authenticated user with pagination.
    """
    user_id = token.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid user.")

    resumes = get_resumes_service(user_id, skip, limit)
    return resumes


@router.delete("/admin/delete_all", status_code=200)
async def delete_all_resumes(token: dict = Depends(verify_token)):
    """
    Delete all resumes (Admin-only).
    """
    if not token.get("is_admin"):
        raise HTTPException(status_code=403, detail="Only admins can perform this action.")

    result = delete_all_resumes_service()
    return result


@router.delete("/{resume_id}", status_code=200)
async def delete_user_resume(
    resume_id: str,
    token: dict = Depends(verify_token),
):
    """
    Delete a specific resume uploaded by the user.
    """
    user_id = token.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid user.")

    result = delete_user_resume_service(user_id, resume_id)
    return result

