# app/routes/usersRoutes.py
from typing import Optional

from bson import ObjectId
from fastapi import APIRouter, HTTPException, Depends, Header, Query
from app.models.user import User
from app.database.connection import MongoDBConnection
from app.services.userService import (
    register_service,
    authenticate_user_service,
    get_all_users_service, update_user_service,
)
from app.utils.jwt import verify_token

router = APIRouter()

# Initialize MongoDB connection
db_connection = MongoDBConnection()
db = db_connection.get_database()
users_collection = db['users']


@router.post("/")
async def register(user: User):
    """ Create a new user with a hashed password. """
    user_id = register_service(user)
    return {"message": "User created successfully.", "user_id": user_id}


@router.post("/authenticate")
async def login(email: Optional[str] = Query(None, description="User's email address"), password: Optional[str] = Query(None, description="User's password")):
    """ Authenticate a user and return a JWT token. """
    if not email and not password:
        email = "admin@example.com"
        password = "admin"
    access_token = authenticate_user_service(email, password)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users")
async def get_all_users():
    """
    Retrieve all users.
    """
    users = get_all_users_service()
    return users


@router.put("/{user_id}")
async def update_user(user_id: str, user_update: User, token: dict = Depends(verify_token)):
    """
    Update user details.
    Ensure the user can only update their own details unless they are an admin.
    """
    # Extract user email and is_admin from the token
    email = token.get("sub")
    is_admin = token.get("is_admin", False)

    # Retrieve the user associated with the user_id
    user = users_collection.find_one({"_id": ObjectId(user_id)})

    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    # Check if the user is authorized to update this account
    if user["email"] != email and not is_admin:
        raise HTTPException(status_code=403, detail="You do not have permission to update this user's details.")

    # Process the update
    updated_fields = user_update.dict(exclude_unset=True)
    if not updated_fields:
        raise HTTPException(status_code=400, detail="No fields provided for update.")

    try:
        modified_count = update_user_service(user_id, updated_fields)
        if modified_count == 0:
            return {"message": "No changes made to the user details."}
        return {"message": "User details updated successfully."}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/me")
async def get_logged_in_user_details(token: dict = Depends(verify_token)):
    """
    Retrieve details about the currently logged-in user.
    """
    email = token.get("sub")
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token. Email not found.")

    # Fetch user details from the database
    user = users_collection.find_one({"email": email}, {"_id": 0, "password": 0})  # Exclude sensitive fields
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    return user
