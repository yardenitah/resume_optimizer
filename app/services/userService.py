from bson import ObjectId
from fastapi import HTTPException
from passlib.hash import bcrypt
from app.database.connection import MongoDBConnection
from app.utils.jwt import create_access_token

# Initialize MongoDB connection
db_connection = MongoDBConnection()
db = db_connection.get_database()
users_collection = db['users']


def create_user_service(user_data):
    """
    Create a new user with a hashed password.
    """
    existing_user = users_collection.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists.")

    # Hash the user's password before storing it
    user_data.password = bcrypt.hash(user_data.password)
    # Insert the new user into MongoDB
    result = users_collection.insert_one(user_data.dict())
    if not result.inserted_id:
        raise HTTPException(status_code=500, detail="Failed to create user.")

    return str(result.inserted_id)


def authenticate_user_service(email: str, password: str):
    """
    Authenticate a user and return a JWT token.
    """
    user = users_collection.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    # Verify the password
    if not bcrypt.verify(password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid credentials.")

    # Generate a JWT token
    return create_access_token(data={"sub": user["email"]})


def get_all_users_service():
    """
    Retrieve all users from the database.
    """
    users = list(users_collection.find())
    for user in users:
        user["id"] = str(user["_id"])
        del user["_id"]
    return users


def get_user_by_id_service(user_id: str):
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


def delete_user_service(user_id: str):
    """
    Delete a user by their ID.
    """
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID.")

    result = users_collection.delete_one({"_id": ObjectId(user_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found.")
    return {"message": "User deleted successfully."}


def delete_all_users_service():
    """
    Delete all users from the database.
    """
    result = users_collection.delete_many({})  # Delete all documents in the collection
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="No users found to delete.")
    return {"message": f"Deleted {result.deleted_count} users."}
