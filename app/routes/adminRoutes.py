# app/routes/adminRoutes.py
from fastapi import APIRouter, HTTPException, Header, Depends
from app.services.adminService import (
    delete_all_users_service,
    get_all_users_service
)
from app.utils.jwt import decode_access_token

router = APIRouter()


def verify_admin(Authorization: str = Header(None)):
    """
    Middleware-like function to verify if the user is an admin using the JWT token.
    """
    print(f"Authorization Header Received: {Authorization}\n")

    if not Authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing.")

    try:
        # Extract the token after 'Bearer'
        token = Authorization.split(" ")[1] if " " in Authorization else Authorization
        payload = decode_access_token(token)  # Decode token
        if not payload.get("is_admin"):
            raise HTTPException(status_code=403, detail="User is not authorized as admin.")
    except ValueError as e:
        raise HTTPException(status_code=403, detail=f"Token Error: {str(e)}")


@router.delete("/users")
async def delete_all_users(Authorization: str = Header(None)):
    verify_admin(Authorization)  # Ensure the user is an admin
    result = delete_all_users_service()
    return result


@router.get("/users")
async def get_all_users(Authorization: str = Header(None)):
    print("Authorization Header Received: ", Authorization)
    verify_admin(Authorization)
    users = get_all_users_service()
    return users
