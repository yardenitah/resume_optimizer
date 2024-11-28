from fastapi import FastAPI
from dotenv import load_dotenv
import os
from app.database.connection import MongoDBConnection

# Load environment variables from the .env file
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Get application name from the environment
app_name = os.getenv("APP_NAME", "Default App")


@app.get("/")
async def root():
    print(f"Root endpoint called. App name: {app_name}")
    return {"message": f"Welcome to {app_name}"}


@app.get("/connect")
async def connect_to_mongo():
    try:
        # Instantiate and connect to MongoDB
        db = MongoDBConnection()
        db.connect()
        return {"message": "Successfully connected to MongoDB!"}
    except Exception as e:
        return {"error": f"Failed to connect to MongoDB: {str(e)}"}
