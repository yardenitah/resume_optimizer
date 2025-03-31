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

    password = user_data.password

    # Verify the password strength
    if not verify_password(password):
        raise HTTPException(status_code=400, detail="Password does not meet the required criteria: \nat least 6 characters, one uppercase letter, and one special character.")

    # Hash the user's password securely
    hashed_password = pwd_context.hash(user_data.password)
    user_data.password = hashed_password

    # Insert the new user into MongoDB
    result = users_collection.insert_one(user_data.dict())
    if not result.inserted_id:
        raise HTTPException(status_code=500, detail="Failed to register the user.")

    newUserToken = authenticate_user_service(user_data.email, password)

    return str(result.inserted_id), newUserToken


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


def search_resumes_by_title_service(user_id: str, title: str, skip: int = 0, limit: int = 10):
    """
    Search resumes by title for a specific user.
    """
    query = {
        "user_id": user_id,
        "title": {"$regex": title, "$options": "i"}  # Case-insensitive search
    }
    resumes = list(resumes_collection.find(query).skip(skip).limit(limit))
    for resume in resumes:
        resume["_id"] = str(resume["_id"])  # Convert ObjectId to string for JSON serialization
    return resumes


def verify_password(password: str) -> bool:
    """
    Verifies if the password meets the following criteria:
    1. At least 6 characters long.
    2. Contains at least one uppercase letter.
    3. Contains at least one special character (e.g., !).

    :param password: The password string to verify.
    :return: True if the password is valid, False otherwise.
    """
    # Define special characters
    special_characters = "!@#$%^&*()-_=+[]{}|;:',.<>?/`~"

    # Check for minimum length
    if len(password) < 6:
        return False

    # Check for at least one uppercase letter
    has_uppercase = False
    for char in password:
        if 'A' <= char <= 'Z':  # Check if char is uppercase
            has_uppercase = True
            break
    if not has_uppercase:
        return False

    # Check for at least one special character
    has_special_char = False
    for char in password:
        if char in special_characters:
            has_special_char = True
            break
    if not has_special_char:
        return False

    return True
