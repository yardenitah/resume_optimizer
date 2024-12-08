# app/main.py
from fastapi.openapi.models import APIKey
from fastapi.openapi.models import SecurityScheme
from fastapi.openapi.utils import get_openapi
from fastapi.security import OAuth2PasswordBearer
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

# Define the OAuth2 scheme for Swagger UI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/authenticate")


def custom_openapi():
    """
    Custom OpenAPI schema to add the 'Authorize' button for JWT token authentication.
    """
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Resume Optimizer API",
        version="1.0.0",
        description="API for managing and optimizing resumes.",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema


# Apply the custom OpenAPI schema
app.openapi = custom_openapi


@app.get("/")
async def root():
    print("message: Welcome to Resume optimizer !!!")
    return {"message: Welcome to Resume optimizer"}
