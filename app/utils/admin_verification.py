# app/utils/admin_verification.py
from fastapi import HTTPException, Header, Depends
from app.utils.jwt import decode_access_token


def verify_admin(Authorization: str = Header(None)):
    """
    Verify if the user is an admin using the JWT token.
    """
    if not Authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing.")

    # Extract the token after 'Bearer'
    scheme, _, token = Authorization.partition(' ')
    if scheme.lower() != 'bearer' or not token:
        raise HTTPException(status_code=401, detail="Invalid token scheme.")

    try:
        payload = decode_access_token(token)  # Decode and validate the token
        if not payload.get("is_admin"):
            raise HTTPException(status_code=403, detail="User is not authorized as admin.")
        return payload
    except ValueError as e:
        raise HTTPException(status_code=403, detail=f"Token Error: {str(e)}")
