import openai
import os
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("CHATGPT_API_KEY")


async def analyze_resume(resume_content: str, job_description: str) -> str:
    # Call OpenAI's ChatGPT API
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert resume reviewer."},
                {"role": "user",
                 "content": f"Analyze this resume: {resume_content} for the following job description: {job_description}"}
            ]
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Failed to analyze resume: {str(e)}"
