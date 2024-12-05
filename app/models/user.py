# app/models/user.py
from pydantic import BaseModel, EmailStr
from datetime import datetime


class User(BaseModel):
    name: str
    email: EmailStr
    password: str
    is_admin: bool = False  # Default to False
    created_at: datetime = datetime.utcnow()  # Automatically set to current UTC time
