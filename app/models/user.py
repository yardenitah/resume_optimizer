from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime


class User(BaseModel):
    name: str
    email: EmailStr
    password: str
    is_admin: bool = True  # Default to False
    created_at: datetime = datetime.utcnow()  # Automatically set to current UTC time
