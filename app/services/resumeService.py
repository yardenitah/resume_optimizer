from bson import ObjectId
from fastapi import HTTPException
from app.database.connection import MongoDBConnection
from app.utils.chatgpt_service import analyze_resume

# Initialize MongoDB connection
db_connection = MongoDBConnection()
db = db_connection.get_database()
resumes_collection = db['resumes']


def create_resume_service(resume_data):
    """
    Create a new resume in the database.
    """
    result = resumes_collection.insert_one(resume_data.dict())
    if not result.inserted_id:
        raise HTTPException(status_code=500, detail="Failed to create resume.")
    return str(result.inserted_id)


def get_all_resumes_service():
    """
    Retrieve all resumes from the database.
    """
    resumes = list(resumes_collection.find())
    for resume in resumes:
        resume["id"] = str(resume["_id"])
        del resume["_id"]
    return resumes


def get_resume_by_id_service(resume_id):
    """
    Retrieve a resume by its ID.
    """
    if not ObjectId.is_valid(resume_id):
        raise HTTPException(status_code=400, detail="Invalid resume ID.")

    resume = resumes_collection.find_one({"_id": ObjectId(resume_id)})
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found.")
    resume["id"] = str(resume["_id"])
    del resume["_id"]
    return resume


def update_resume_service(resume_id, updated_resume):
    """
    Update an existing resume by its ID.
    """
    if not ObjectId.is_valid(resume_id):
        raise HTTPException(status_code=400, detail="Invalid resume ID.")

    result = resumes_collection.update_one(
        {"_id": ObjectId(resume_id)},
        {"$set": updated_resume.dict()}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Resume not found or no changes made.")
    return {"message": "Resume updated successfully."}


def delete_resume_service(resume_id):
    """
    Delete a resume by its ID.
    """
    if not ObjectId.is_valid(resume_id):
        raise HTTPException(status_code=400, detail="Invalid resume ID.")

    result = resumes_collection.delete_one({"_id": ObjectId(resume_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Resume not found.")
    return {"message": "Resume deleted successfully."}


async def analyze_resume_service(resume_id, job_description):
    """
    Analyze a resume for a specific job description using ChatGPT.
    """
    if not ObjectId.is_valid(resume_id):
        raise HTTPException(status_code=400, detail="Invalid resume ID.")

    resume = resumes_collection.find_one({"_id": ObjectId(resume_id)})
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found.")

    return await analyze_resume(resume["content"], job_description)
