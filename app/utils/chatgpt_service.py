# app/utils/chatgpt_service.py
import openai
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")


async def analyze_resume(resume_content: str, job_description: str, job_title: str) -> str:
    """
    Analyze a resume against a job description using OpenAI's ChatGPT API.

    Args:
        resume_content (str): The content of the user's resume.
        job_description (str): The job description to compare the resume against.
        job_title (str): The title of the job.

    Returns:
        str: AI-generated analysis or suggestions.
    """
    try:
        # Call OpenAI's ChatGPT API
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert in evaluating resumes for job applications."},
                {
                    "role": "user",
                    "content": (
                        f"Please analyze the following resume for the job title '{job_title}'. "
                        f"Provide feedback on how well it aligns with the job description "
                        f"and suggest improvements.\n\n"
                        f"Resume Content:\n{resume_content}\n\n"
                        f"Job Description:\n{job_description}"
                    ),
                },
            ],
            max_tokens=50
        )
        # Return the AI-generated analysis
        return response.choices[0].message.content.strip()
    except Exception as e:
        # Handle exceptions
        return f"Failed to analyze resume: {str(e)}"


async def calculate_match_score(resume_content: str, job_description: str, job_title: str) -> float:
    """
    Calculate a match score for a resume based on a job description using OpenAI's ChatGPT API.

    Args:
        resume_content (str): The content of the resume.
        job_description (str): The job description to compare the resume against.
        job_title (str): The title of the job.

    Returns:
        float: A score representing how well the resume matches the job description.
    """
    try:
        # Call OpenAI's ChatGPT API for scoring
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert in evaluating resumes for job applications."},
                {
                    "role": "user",
                    "content": (
                        f"Please evaluate the following resume for the job title '{job_title}'. "
                        f"Rate its suitability for the job description on a scale from 0 to 100.\n\n"
                        f"Resume Content:\n{resume_content}\n\n"
                        f"Job Description:\n{job_description}"
                    ),
                },
            ],
            max_tokens=2
        )
        # Parse and return the score
        analysis = response.choices[0].message.content.strip()
        score = float(analysis.split("Score:")[-1].strip())  # Extract the score
        return score
    except Exception as e:
        return -1.0  # Return a negative score if an error occurs
