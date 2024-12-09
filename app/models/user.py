# app/models/user.py
from typing import Optional
from pydantic import BaseModel, EmailStr
from datetime import datetime


class User(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str]
    is_admin: bool = False  # Default to False
    created_at: datetime = datetime.utcnow()  # Automatically set to current UTC time
