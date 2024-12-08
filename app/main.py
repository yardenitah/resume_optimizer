# app/main.py
from fastapi import FastAPI
from dotenv import load_dotenv
import os
from app.database.connection import MongoDBConnection
from app.routes import usersRouts, resumeRouts, adminRoutes

# Load environment variables from the .env file
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Include routers
app.include_router(usersRouts.router, prefix="/users", tags=["Users"])
app.include_router(resumeRouts.router, prefix="/resumes", tags=["Resumes"])
app.include_router(adminRoutes.router, prefix="/admin", tags=["Admin"])


@app.get("/")
async def root():
    print("message: Welcome to Resume optimizer !!!")
    return {"message: Welcome to Resume optimizer"}
