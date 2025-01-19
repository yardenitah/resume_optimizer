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


import asyncio
import logging
import openai

async def analyze_resume(resume_content: str, job_description: str, job_title: str) -> str:
    """
    Analyze the resume for a given job, returning a concise response
    divided into 3 short parts:
      1) What to emphasize/improve in the resume.
      2) The resume's best points for the job.
      3) Recommendation on submitting the resume.
    """
    try:
        # Instruct GPT-4 to break its answer into 3 short parts.
        # Using max_tokens to limit length (adjust as needed).
        prompt = (
            f"Analyze this resume for the job title '{job_title}'. "
            "Provide feedback in exactly 3 concise sections:\n\n"
            "1) Emphasize/Improve: Which areas should the candidate emphasize or improve?\n"
            "2) Best Points: What are the strongest points in the resume for this job?\n"
            "3) Recommendation: Should the candidate submit this resume for the job or not "
             "(just 'I recommend to submit' or 'I do not recommend to submit')?\n\n"
            "Keep the overall answer short, relevant, and avoid redundancy.\n\n"
            f"Resume Content:\n{resume_content}\n\n"
            f"Job Description:\n{job_description}"
        )

        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert in evaluating resumes for job applications."
                },
                {
                    "role": "user",
                    "content": prompt
                },
            ],
            max_tokens=400,   # Increase or decrease depending on how concise you want the result
            temperature=0.7,  # Adjust creativity; 0 is most factual, 1 is more creative
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
