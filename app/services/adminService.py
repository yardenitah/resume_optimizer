# app/services/adminService.py
from bson import ObjectId
from fastapi import HTTPException
from app.database.connection import MongoDBConnection

# Initialize MongoDB connection
db_connection = MongoDBConnection()
db = db_connection.get_database()
users_collection = db['users']


def delete_all_users_admin_service():
    """
    Delete all users from the database.
    """
    result = users_collection.delete_many({})  # Delete all users
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="No users found to delete.")
    return {"message": f"Deleted {result.deleted_count} users."}


def get_all_users_admin_service():
    """
    Retrieve all users from the database.
    """
    users = list(users_collection.find())
    print("the len of user list :", len(users))
    for user in users:
        user["id"] = str(user["_id"])
        del user["_id"]
    return users


def get_user_by_id_admin_service(user_id: str):
    """
    Retrieve a single user by their ID.
    """
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID.")

    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    user["id"] = str(user["_id"])
    del user["_id"]
    return user


def delete_user_admin_service(user_id: str):
    """
    Delete a user by their ID.
    """
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID.")

    result = users_collection.delete_one({"_id": ObjectId(user_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found.")
    return {"message": "User deleted successfully."}
