# app/services/userService.py
from bson import ObjectId
from fastapi import HTTPException
from passlib.hash import bcrypt
from pydantic import EmailStr

from app.database.connection import MongoDBConnection
from app.models.user import User
from app.services.resumeService import resumes_collection
from app.utils.jwt import create_access_token
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Initialize MongoDB connection
db_connection = MongoDBConnection()
db = db_connection.get_database()
users_collection = db['users']


def register_service(user_data: User):
    """
    Create a new user with a hashed password.
    """
    # Ensure email uniqueness
    existing_user = users_collection.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="A user with this email already exists.")

    # Hash the user's password securely
    hashed_password = pwd_context.hash(user_data.password)
    user_data.password = hashed_password

    # Insert the new user into MongoDB
    result = users_collection.insert_one(user_data.dict())
    if not result.inserted_id:
        raise HTTPException(status_code=500, detail="Failed to register the user.")

    return str(result.inserted_id)


# use fir login
def authenticate_user_service(email: EmailStr, password: str):
    """
    Authenticate a user and return a JWT token.
    """
    user = users_collection.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    # Verify the password
    if not pwd_context.verify(password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password.")

    # Generate a JWT token
    token = create_access_token(data={
        "sub": user["email"],
        "is_admin": user.get("is_admin", False),
        "user_id": str(user["_id"])  # Include user_id in the token
    })

    return {"access_token": token, "token_type": "bearer"}


def get_all_users_service():
    """ Retrieve all users from the database. """
    users = list(users_collection.find())
    print("the len of user list :", len(users))
    for user in users:
        user["id"] = str(user["_id"])
        del user["_id"]
    return users


def update_user_service(user_id: str, updated_fields: dict):
    """ Update user details, ensuring the password is hashed correctly. """
    if not ObjectId.is_valid(user_id):
        raise ValueError("Invalid user ID format.")

    # Check if password is being updated
    if "password" in updated_fields:
        # Hash the password only if it isn't already hashed
        if not pwd_context.identify(updated_fields["password"]):
            updated_fields["password"] = bcrypt.hash(updated_fields["password"])

    result = users_collection.update_one({"_id": ObjectId(user_id)}, {"$set": updated_fields})

    if result.matched_count == 0:
        raise ValueError("User not found.")

    return result.modified_count


