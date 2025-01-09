# app/utils/chatgpt_service.py
import openai
import asyncio
import os
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Set OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")


# async def analyze_resume(resume_content: str, job_description: str, job_title: str) -> str:
#     try:
#         # Call OpenAI's ChatGPT API
#         response = openai.ChatCompletion.create(
#             model="gpt-4",
#             messages=[
#                 {"role": "system", "content": "You are an expert in evaluating resumes for job applications."},
#                 {
#                     "role": "user",
#                     "content": (
#                         f"Please analyze the following resume for the job title '{job_title}'. "
#                         f"Provide feedback on how well it aligns with the job description "
#                         f"and suggest improvements.\n\n"
#                         f"Resume Content:\n{resume_content}\n\n"
#                         f"Job Description:\n{job_description}"
#                     ),
#                 },
#             ],
#             max_tokens=90
#         )
#         # Return the AI-generated analysis
#         return response.choices[0].message.content.strip()
#     except Exception as e:
#         # Handle exceptions
#         return f"Failed to analyze resume: {str(e)}"


async def analyze_resume(resume_content: str, job_description: str, job_title: str) -> str:
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert in evaluating resumes for job applications."},
                {
                    "role": "user",
                    "content": (
                        f"Analyze this resume for the job title '{job_title}'. Provide feedback "
                        f"on how it aligns with the job description and suggest improvements.\n\n"
                        f"Resume:\n{resume_content}\n\n"
                        f"Job Description:\n{job_description}"
                    ),
                },
            ],
            max_tokens=100,
        )
        return response.choices[0].message.content.strip()
    except openai.error.RateLimitError:
        logging.error("Rate limit reached. Retrying after a delay.")
        await asyncio.sleep(3)  # Delay before retrying
        return await analyze_resume(resume_content, job_description, job_title)
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
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
                        f"Rate its suitability for the job description on a scale from 0 to 100. "
                        f"Respond with the numerical score only.\n\n"
                        f"Resume Content:\n{resume_content}\n\n"
                        f"Job Description:\n{job_description}"
                    ),
                },
            ],
            max_tokens=5  # Small token limit for numerical score
        )
        # Extract and convert the score
        score_text = response.choices[0].message.content.strip()
        # print(f"score text: {score_text}\n all the response: \n \n {response.choices}")
        return float(score_text)
    except Exception as e:
        # Log the error and return a default negative score
        logging.error(f"Error calculating match score: {str(e)}")
        return -1.0
