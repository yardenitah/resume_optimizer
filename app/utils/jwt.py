# app/utils/jwt.py
from datetime import datetime, timedelta
from jose import jwt, JWTError
from fastapi import HTTPException, Header
from dotenv import load_dotenv
import os

load_dotenv()

# Constants for JWT
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 120


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    print(f"Data for create_access_token: {data}")  # Debugging output
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """
    Decode a JWT access token and verify its validity.
    """
    try:
        print(f"Token for decode_access_token: {token}")  # Debugging output
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"Decoded payload: {payload}")  # Debugging output
        return payload
    except JWTError as e:
        raise ValueError("Invalid or expired token.")


def verify_token(Authorization: str = Header(None)):
    """
    Dependency function to verify the JWT token.
    """
    if not Authorization:
        raise HTTPException(status_code=401, detail="Authorization header missing.")

    # Extract the token after 'Bearer'
    scheme, _, token = Authorization.partition(' ')
    print(f"Authorization Header - Scheme: {scheme}, Token: {token}")  # Debugging output
    if scheme.lower() != 'bearer' or not token:
        raise HTTPException(status_code=401, detail="Invalid token scheme.")

    try:
        payload = decode_access_token(token)  # Decode and validate the token
        if not payload.get("user_id"):
            raise HTTPException(status_code=401, detail="Invalid token. Missing user_id.")
        return payload
    except ValueError as e:
        raise HTTPException(status_code=403, detail=f"Token Error: {str(e)}")
