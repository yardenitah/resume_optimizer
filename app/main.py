# /Users/yardenmac/Desktop/Software/Pycharm/resume_optimizer/app/main.py
import openai
from fastapi.middleware.cors import CORSMiddleware  # Import CORS middleware
from fastapi.openapi.utils import get_openapi
from fastapi.security import OAuth2PasswordBearer
from fastapi import FastAPI
from dotenv import load_dotenv
import os
from app.routes import usersRouts, resumeRouts, adminRoutes, jobRoutes

# Load environment variables from the .env file
load_dotenv()

# Initialize FastAPI
app = FastAPI()
# Configure CORS
origins = [
    "http://resume-optimizer-resumes.s3-website.eu-central-1.amazonaws.com",
    "https://resume-optimizer-resumes.s3-website.eu-central-1.amazonaws.com",
    "http://localhost:3000",  # React frontend
    "http://127.0.0.1:3000",  # Alternative local React frontend
    "https://d3n5er3xfm3yco.cloudfront.net" # cloud front domain
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Allows all origins
    allow_credentials=False,  # Must be False if allow_origins=["*"]
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Load OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
uri = os.getenv("MONGO_URI")
print(uri)
# Set the API key
openai.api_key = OPENAI_API_KEY
print(f"OpenAI API Key: {OPENAI_API_KEY}")
# Include routers
app.include_router(usersRouts.router, prefix="/api/users", tags=["Users"])
app.include_router(jobRoutes.router, prefix="/api/jobs", tags=["Jobs"])
app.include_router(resumeRouts.router, prefix="/api/resumes", tags=["Resumes"])
app.include_router(adminRoutes.router, prefix="/api/admin", tags=["Admin"])

# Define the OAuth2 scheme for Swagger UI
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/users/authenticate")


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
async def check_openai_key():
    try:
        print("Checking OpenAI API key...")
        # Make a real request to OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-4o",  # You can change to gpt-3.5-turbo if you want to save money
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Say hello!"}
            ]
        )
        message = response.choices[0].message["content"].strip()
        return {
            "status": "success",
            "message": "API Key is valid!",
            "response": message
        }
    except openai.error.AuthenticationError:
        return {
            "status": "error",
            "message": "Invalid API Key! Please check your key and try again."
        }
    except openai.error.RateLimitError:
        return {
            "status": "error",
            "message": "Quota exceeded. Please check your OpenAI usage and billing."
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"An error occurred: {e}"
        }
