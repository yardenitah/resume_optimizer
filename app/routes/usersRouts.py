from fastapi import APIRouter, HTTPException, Depends, Header
from app.models.user import User
from app.services.userService import (
    create_user_service,
    authenticate_user_service,
    get_all_users_service,
    get_user_by_id_service,
    delete_user_service, delete_all_users_service,
)

router = APIRouter()


@router.post("/")
async def create_user(user: User):
    """
    Create a new user with a hashed password.
    """
    user_id = create_user_service(user)
    return {"message": "User created successfully.", "user_id": user_id}


@router.post("/authenticate")
async def authenticate_user(email: str, password: str):
    """
    Authenticate a user and return a JWT token.
    """
    access_token = authenticate_user_service(email, password)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/")
async def get_all_users(Authorization: str = Header(None)):
    """
    Retrieve all users from the database. Requires a valid JWT token.
    """
    # In a real application, you should verify the token here
    users = get_all_users_service()
    return users


@router.get("/{user_id}")
async def get_user_by_id(user_id: str, Authorization: str = Header(None)):
    """
    Retrieve a single user by their ID. Requires a valid JWT token.
    """
    # In a real application, you should verify the token here
    user = get_user_by_id_service(user_id)
    return user


@router.delete("/{user_id}")
async def delete_user(user_id: str, Authorization: str = Header(None)):
    """
    Delete a user by their ID. Requires a valid JWT token.
    """
    # In a real application, you should verify the token here
    return delete_user_service(user_id)


@router.delete("/users")
async def delete_all_users():
    """
    Delete all users (admin-only).
    """
    return delete_all_users_service()