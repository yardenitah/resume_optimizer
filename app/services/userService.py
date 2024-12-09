# app/services/userService.py
from bson import ObjectId
from fastapi import HTTPException
from passlib.hash import bcrypt
from app.database.connection import MongoDBConnection
from app.utils.jwt import create_access_token
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Initialize MongoDB connection
db_connection = MongoDBConnection()
db = db_connection.get_database()
users_collection = db['users']


def register_service(user_data):
    """
    Create a new user with a hashed password.
    """
    existing_user = users_collection.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists.")

    # Hash the user's password before storing it
    user_data.password = bcrypt.hash(user_data.password)
    # Insert the new user into MongoDB
    result = users_collection.insert_one(user_data.dict())
    if not result.inserted_id:
        raise HTTPException(status_code=500, detail="Failed to create user.")

    return str(result.inserted_id)


def authenticate_user_service(email: str, password: str):
    """
    Authenticate a user and return a JWT token. use in login route
    """
    user = users_collection.find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    # Verify the password
    if not bcrypt.verify(password, user["password"]):
        raise HTTPException(status_code=401, detail="Invalid password.")

    # Generate a JWT token from jwt file, including the is_admin field
    token = create_access_token(data={"sub": user["email"], "is_admin": user.get("is_admin", False)})

    return token


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