from fastapi import FastAPI
from dotenv import load_dotenv
import os
from app.database.connection import MongoDBConnection
from app.routes import usersRouts, resumeRouts

# Load environment variables from the .env file
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Include routers
app.include_router(usersRouts.router, prefix="/users", tags=["Users"])
app.include_router(resumeRouts.router, prefix="/resumes", tags=["Resumes"])

# Application metadata
app_name = os.getenv("APP_NAME", "Resume Optimizer")


@app.get("/")
async def root():
    return {"message": f"Welcome to {app_name}"}
