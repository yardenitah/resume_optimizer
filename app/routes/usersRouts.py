# app/routes/usersRoutes.py
from fastapi import APIRouter, HTTPException, Depends, Header
from app.models.user import User
from app.services.userService import (
    create_user_service,
    authenticate_user_service,
    get_all_users_service,
    get_user_by_id_service,
    delete_user_service,
)
from app.utils.jwt import decode_access_token

router = APIRouter()


def verify_token(Authorization: str = Header(None)):
    """
    Dependency function to verify the JWT token.
    """
    if not Authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing.")

    try:
        # Extract the token after 'Bearer '
        scheme, _, token = Authorization.partition(' ')
        if scheme.lower() != 'bearer' or not token:
            raise HTTPException(status_code=401, detail="Invalid token scheme.")

        payload = decode_access_token(token)  # Decode the token
        return payload
    except ValueError as e:
        raise HTTPException(status_code=403, detail=f"Token Error: {str(e)}")


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
async def get_all_users(payload=Depends(verify_token)):
    """
    Retrieve all users from the database. Requires a valid JWT token.
    """
    users = get_all_users_service()
    return users


@router.get("/{user_id}")
async def get_user_by_id(user_id: str, payload=Depends(verify_token)):
    """
    Retrieve a single user by their ID. Requires a valid JWT token.
    """
    user = get_user_by_id_service(user_id)
    return user


@router.delete("/{user_id}")
async def delete_user(user_id: str, payload=Depends(verify_token)):
    """
    Delete a user by their ID. Requires a valid JWT token.
    """
    return delete_user_service(user_id)
