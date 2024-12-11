# app/services/resumeService.py
from app.utils.s3_service import upload_file_to_s3, AWS_S3_BUCKET, generate_presigned_url, extract_file_key, s3_client
from app.database.connection import MongoDBConnection
from bson import ObjectId
from datetime import datetime
from fastapi import HTTPException
from bson.errors import InvalidId


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


db_connection = MongoDBConnection()
db = db_connection.get_database()
resumes_collection = db["resumes"]


def upload_resume_service(user_id: str, file, title: str, file_extension: str):
    """
    Handle the uploading of a resume file.
    """
    # Upload file to S3 and get the S3 URL
    s3_url = upload_file_to_s3(file, user_id, file_extension)

    # Save metadata in MongoDB, including the S3 URL
    resume_data = {
        "user_id": user_id,
        "title": title,
        "content": "",  # Optional: Can be filled later with parsed resume content
        "s3_url": s3_url,  # Save the S3 URL here
        "created_at": datetime.utcnow(),
    }
    result = resumes_collection.insert_one(resume_data)
    if not result.inserted_id:
        raise HTTPException(status_code=500, detail="Failed to save resume in database.")

    return {"message": "Resume uploaded successfully.", "s3_url": s3_url}


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


def delete_user_resume_service(user_id: str, resume_id: str):
    """
    Delete a specific resume uploaded by the user.
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

        return {"message": "Resume deleted successfully."}
    except InvalidId:
        raise HTTPException(status_code=400, detail="Invalid resume ID.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
