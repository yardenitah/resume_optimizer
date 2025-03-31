# app/services/resumeService.py
from app.utils.chatgpt_service import calculate_match_score
from app.utils.file_extractor import extract_text_from_file
from app.utils.s3_service import upload_file_to_s3, AWS_S3_BUCKET, generate_presigned_url, extract_file_key, s3_client
from app.database.connection import MongoDBConnection
from bson import ObjectId
from datetime import datetime
from fastapi import HTTPException
from bson.errors import InvalidId

db_connection = MongoDBConnection()
db = db_connection.get_database()
resumes_collection = db["resumes"]



def upload_resume_service(user_id: str, file, title: str, file_extension: str):
    """
    Handle the uploading of a resume file.
    """
    # Extract text content from the file
    text_content = ""
    try:
        text_content = extract_text_from_file(file, file_extension)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to extract text: {str(e)}")
    print(f"\n\ntext content: {text_content}\n\n")

    # Reset file pointer before uploading to S3
    file.seek(0)
    # Upload file to S3 and get the S3 URL
    s3_url = upload_file_to_s3(file, user_id, file_extension)

    # Save metadata in MongoDB, including the S3 URL and initialize job_ids
    resume_data = {
        "user_id": user_id,
        "title": title,
        "content": text_content,  # Save extracted text here
        "s3_url": s3_url,  # Save the S3 URL here
        "job_ids": [],       # Initialize job_ids as an empty list
        "created_at": datetime.utcnow(),
    }
    result = resumes_collection.insert_one(resume_data)
    if not result.inserted_id:
        raise HTTPException(status_code=500, detail="Failed to save resume in database.")

    return {"message": "Resume uploaded successfully.", "s3_url": s3_url}


def delete_all_resumes_service():
    """
    Delete all resumes from both the database and S3 (Admin only).
    """
    # Fetch all resumes from MongoDB to extract S3 file keys
    all_resumes = resumes_collection.find()
    file_keys = []

    # Extract the file keys from S3 URLs
    for resume in all_resumes:
        s3_url = resume.get("s3_url")
        if s3_url:
            try:
                file_key = extract_file_key(s3_url)
                file_keys.append(file_key)
            except ValueError as e:
                print(f"Invalid S3 URL format: {s3_url}, Error: {str(e)}")  # Log invalid URLs

    # Delete files from S3
    if file_keys:
        try:
            delete_objects = [{"Key": key} for key in file_keys]
            s3_client.delete_objects(
                Bucket=AWS_S3_BUCKET,
                Delete={"Objects": delete_objects}
            )
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete files from S3: {str(e)}")

    # Delete all records from MongoDB
    result = resumes_collection.delete_many({})
    return {"message": f"Deleted {result.deleted_count} resumes from MongoDB and corresponding files from S3."}


def get_resumes_service(user_id: str, skip: int = 0, limit: int = 10):
    """
    Retrieve all resumes uploaded by a specific user from MongoDB with pagination.
    """
    resumes = list(resumes_collection.find({"user_id": user_id}).skip(skip).limit(limit))
    for resume in resumes:
        resume["_id"] = str(resume["_id"])  # Convert ObjectId to string for JSON serialization
    return resumes


def get_presigned_url_service(user_id: str, resume_id: str, expiration: int):
    """
    Generate a pre-signed URL for a specific user's resume.
    """
    # Find the resume in MongoDB
    resume = resumes_collection.find_one({"_id": ObjectId(resume_id), "user_id": user_id})
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found or unauthorized access.")

    # Extract the file key from the S3 URL
    s3_url = resume.get("s3_url")
    if not s3_url:
        raise HTTPException(status_code=500, detail="Resume does not have a valid S3 URL.")

    file_key = extract_file_key(s3_url)
    presigned_url = generate_presigned_url(file_key, expiration)
    return presigned_url


def get_all_user_resumes_service(user_id: str, skip: int = 0, limit: int = 10):
    """
    Retrieve all resumes uploaded by a specific user with pagination.
    """
    resumes = list(resumes_collection.find({"user_id": user_id}).skip(skip).limit(limit))
    for resume in resumes:
        resume["_id"] = str(resume["_id"])  # Convert ObjectId to string for JSON serialization
    return resumes


def delete_user_resume_service(user_id: str, resume_id: str):
    """
    Delete a specific resume uploaded by the user,
    and if it was the best resume for any job,
    remove that reference from the job.
    """
    try:
        resume = resumes_collection.find_one({"_id": ObjectId(resume_id), "user_id": user_id})
        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found or unauthorized access.")

        # Extract the file key from the S3 URL
        s3_url = resume.get("s3_url")
        file_key = s3_url.split(f"https://{AWS_S3_BUCKET}.s3.amazonaws.com/")[-1]

        # Delete the file from S3
        try:
            s3_client.delete_object(Bucket=AWS_S3_BUCKET, Key=file_key)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to delete file from S3: {str(e)}")

        # Delete the resume from MongoDB
        result = resumes_collection.delete_one({"_id": ObjectId(resume_id), "user_id": user_id})
        if result.deleted_count == 0:
            raise HTTPException(status_code=500, detail="Failed to delete resume from database.")

        # NEW: If this resume was the best_resume_id for any jobs, remove that reference.
        from app.services.jobService import jobs_collection  # or import at top of file
        jobs_collection.update_many(
            {"best_resume_id": str(resume_id)},
            {"$unset": {"best_resume_id": ""}}
        )

        return {"message": "Resume deleted successfully."}

    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid resume ID.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


def search_resumes_by_title_service(user_id: str, title: str, skip: int = 0, limit: int = 10):
    """
    Search resumes by title for a specific user.
    """
    query = {
        "user_id": user_id,
        "title": {"$regex": title, "$options": "i"}  # Case-insensitive search
    }
    resumes = list(resumes_collection.find(query).skip(skip).limit(limit))
    for resume in resumes:
        resume["_id"] = str(resume["_id"])  # Convert ObjectId to string for JSON serialization
    return resumes


def get_resume_by_id_service(user_id: str, resume_id: str):
    """
    Retrieve a specific resume by ID for a user.
    """
    try:
        resume = resumes_collection.find_one({"_id": ObjectId(resume_id), "user_id": user_id})
        if resume:
            resume["_id"] = str(resume["_id"])  # Convert ObjectId to string
        return resume
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching resume: {str(e)}")


async def find_best_resume_service(user_id: str, job_description: str, job_title: str):
    # Retrieve all resumes for the user
    resumes = list(resumes_collection.find({"user_id": user_id}))
    if not resumes:
        raise HTTPException(status_code=404, detail="No resumes found for the user.")

    best_resume = None
    highest_score = -1

    for resume in resumes:
        resume_content = resume.get("content", "")
        if not resume_content:
            continue  # Skip resumes without content

        # Get the match score using ChatGPT
        score = await calculate_match_score(resume_content, job_description, job_title)
        resume["score"] = score  # Update the resume with the score

        if score > highest_score:
            highest_score = score
            best_resume = resume

    if not best_resume:
        raise HTTPException(status_code=404, detail="No suitable resume found.")

    return {
        "best_resume": {
            "id": str(best_resume["_id"]),
            "title": best_resume["title"],
            "score": best_resume["score"],
            "s3_url": best_resume.get("s3_url"),
        },
        "all_resumes": [
            {
                "id": str(resume["_id"]),
                "title": resume["title"],
                "score": resume.get("score"),
                "s3_url": resume.get("s3_url"),
            }
            for resume in resumes
        ],
    }


def add_job_to_resume_service(resume_id: str, job_id: str):
    """
    Associate a Job ID with a Resume by updating the Resume's job_ids list.
    """
    try:
        result = resumes_collection.update_one(
            {"_id": ObjectId(resume_id)},
            {"$addToSet": {"job_ids": job_id}}  # Use $addToSet to avoid duplicates
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Resume not found.")
        if result.modified_count == 0:
            print(f"Job ID {job_id} was already associated with Resume ID {resume_id}.")
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid resume ID.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to associate job with resume: {str(e)}")


def remove_job_from_resume_service(resume_id: str, job_id: str):
    """
    Remove a Job ID from a Resume's job_ids list.
    """
    try:
        result = resumes_collection.update_one(
            {"_id": ObjectId(resume_id)},
            {"$pull": {"job_ids": job_id}}  # $pull removes the item from the array
        )
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Resume not found.")
        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Job ID not associated with this resume.")
        return {"message": f"Job ID {job_id} removed from Resume ID {resume_id} successfully."}
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid resume ID.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove job from resume: {str(e)}")

async def get_jobs_id_of_resume_service(user_id: str, resume_id: str) -> list:
    """
    Retrieve the list of Job IDs associated with a specific Resume.

    Args:
        user_id (str): ID of the user.
        resume_id (str): ID of the resume.

    Returns:
        list: List of associated Job IDs.
    """
    try:
        # Fetch the resume document from MongoDB
        resume = resumes_collection.find_one({"_id": ObjectId(resume_id), "user_id": user_id})

        if not resume:
            raise HTTPException(status_code=404, detail="Resume not found or unauthorized access.")

        # Return the job_ids field
        return resume.get("job_ids", [])

    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid resume ID.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch job IDs: {str(e)}")
