# app/utils/jwt.py
from fastapi import APIRouter, HTTPException, Depends, Header
from datetime import datetime, timedelta
from jose import jwt, JWTError
from dotenv import load_dotenv
import os

load_dotenv()

# Constants for JWT
# SECRET_KEY = "your-secret-key"
SECRET_KEY = os.getenv("JWT_SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    to_encode = data.copy()
    print(f"data from create_access_token function {data}")
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """Decode a JWT access token and verify its validity."""
    try:
        print(f"token from decode_access_token function {token}")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        print(f"payload from decode_access_token function {payload}")
        return payload
    except JWTError:
        raise ValueError("Invalid or expired token.")


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
