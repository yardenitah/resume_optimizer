# app/services/adminService.py
from fastapi import HTTPException
from app.database.connection import MongoDBConnection

# Initialize MongoDB connection
db_connection = MongoDBConnection()
db = db_connection.get_database()
users_collection = db['users']


def delete_all_users_service():
    """
    Delete all users from the database.
    """
    result = users_collection.delete_many({})  # Delete all users
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="No users found to delete.")
    return {"message": f"Deleted {result.deleted_count} users."}


def get_all_users_service():
    """
    Retrieve all users from the database.
    """
    users = list(users_collection.find())
    for user in users:
        user["id"] = str(user["_id"])  # Convert ObjectId to string
        del user["_id"]  # Remove MongoDB-specific ID
    return users
