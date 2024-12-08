# app/routes/usersRoutes.py
from fastapi import APIRouter, HTTPException, Depends, Header
from app.models.user import User
from app.services.userService import (
    register_service,
    authenticate_user_service, get_all_users_service,
)
from app.utils.jwt import decode_access_token

router = APIRouter()


def verify_token(Authorization: str = Header(None)):
    """
    Dependency function to verify the JWT token.
    """
    if not Authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing.")

    # Extract the token after 'Bearer'
    scheme, _, token = Authorization.partition(' ')
    if scheme.lower() != 'bearer' or not token:
        raise HTTPException(status_code=401, detail="Invalid token scheme.")

    try:
        payload = decode_access_token(token)  # Decode and validate the token
        return payload
    except ValueError as e:
        raise HTTPException(status_code=403, detail=f"Token Error: {str(e)}")


@router.post("/")
async def register(user: User):
    """
    Create a new user with a hashed password.
    """
    user_id = register_service(user)
    return {"message": "User created successfully.", "user_id": user_id}


@router.post("/authenticate")
async def login():
    """
    Authenticate a user and return a JWT token.
    """
    # delete !!
    email = "yarden1606@gmail.com"
    password = "Yarden1169!"
    access_token = authenticate_user_service(email, password)
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/users")
async def get_all_users():
    """
    Retrieve all users. Admin access required.
    """
    users = get_all_users_service()
    return users
