# app/routes/usersRoutes.py
from typing import Optional

from bson import ObjectId
from fastapi import APIRouter, HTTPException, Depends, Header, Query
from pydantic import EmailStr

from app.models.user import User
from app.database.connection import MongoDBConnection
from app.services.userService import (
    register_service,
    authenticate_user_service,
    get_all_users_service, update_user_service, pwd_context,
)
from app.utils.jwt import verify_token
from app.utils.validation import validate_update_payload

router = APIRouter()

# Initialize MongoDB connection
db_connection = MongoDBConnection()
db = db_connection.get_database()
users_collection = db['users']


@router.post("/register", status_code=201)
async def register(user: User):
    """
    Register a new user with hashed password.
    """
    user_id = register_service(user)
    return {"message": "User registered successfully.", "user_id": user_id}


@router.post("/login", status_code=200)
async def login(email: EmailStr, password: str):
    """
    Authenticate a user and return a JWT token.
    """
    token_data = authenticate_user_service(email, password)
    return token_data


@router.get("/users")
async def get_all_users():
    """
    Retrieve all users.
    """
    users = get_all_users_service()
    return users


@router.put("/{user_id}", response_model=dict)
async def update_user(user_id: str, user_update: dict, token: dict = Depends(verify_token)):
    """
    Update user details.
    Ensure only allowed fields are updated, and restrict updates to self unless admin.
    """
    email = token.get("sub")
    is_admin = token.get("is_admin", False)

    # Validate user_id format
    if not ObjectId.is_valid(user_id):
        raise HTTPException(status_code=400, detail="Invalid user ID format.")

    # Fetch user from database
    user = users_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    # Ensure the logged-in user is authorized to update this user
    if user["email"] != email and not is_admin:
        raise HTTPException(status_code=403, detail="Permission denied.")

    # Validate the update payload
    allowed_fields = {"name", "password", "email"}
    updated_fields = validate_update_payload(user_update, allowed_fields)

    # Validate email uniqueness if updating email
    if "email" in updated_fields:
        new_email = updated_fields["email"]
        if users_collection.find_one({"email": new_email, "_id": {"$ne": ObjectId(user_id)}}):
            raise HTTPException(status_code=400, detail="This email is already in use.")

    # Hash the password if it's being updated
    if "password" in updated_fields:
        updated_fields["password"] = pwd_context.hash(updated_fields["password"])

    if not updated_fields:
        raise HTTPException(status_code=400, detail="No valid fields provided for update.")

    # Perform the update
    result = users_collection.update_one({"_id": ObjectId(user_id)}, {"$set": updated_fields})
    if result.matched_count == 0:
        raise HTTPException(status_code=500, detail="Failed to update user details.")

    return {"message": "User details updated successfully."}


@router.get("/me", response_model=dict)
async def get_logged_in_user_details(token: dict = Depends(verify_token)):
    """
    Retrieve details about the currently logged-in user.
    """
    email = token.get("sub")
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token. Missing email.")

    # Fetch user details from the database
    user = users_collection.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    # Convert ObjectId to string and remove sensitive fields
    user_data = {
        "id": str(user["_id"]),
        "name": user["name"],
        "email": user["email"],
        "is_admin": user.get("is_admin", False),
        "created_at": user.get("created_at")
    }
    return {"user": user_data}
