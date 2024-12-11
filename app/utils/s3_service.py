# app/utils/s3_service.py
import boto3
from botocore.exceptions import NoCredentialsError
import uuid
from fastapi import HTTPException
from dotenv import load_dotenv
import os

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_S3_BUCKET = os.getenv("AWS_S3_BUCKET")

s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name='eu-central-1',  # Your S3 bucket's region
    endpoint_url='https://s3.eu-central-1.amazonaws.com'  # Regional endpoint
)


def upload_file_to_s3(file, user_id: str, file_extension: str) -> str:
    """Upload a file to S3 and return its URL. """
    try:
        # Generate a unique filename
        filename = f"{user_id}/{uuid.uuid4()}.{file_extension}"
        print(f"Generated S3 file key: {filename}")  # Debug log

        # Upload the file without ACLs
        s3_client.upload_fileobj(
            file,
            AWS_S3_BUCKET,
            filename
        )
        s3_url = f"https://{AWS_S3_BUCKET}.s3.amazonaws.com/{filename}"
        print(f"File uploaded successfully. URL: {s3_url}")  # Debug log
        return s3_url
    except NoCredentialsError:
        raise HTTPException(status_code=500, detail="AWS credentials not found.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")


def generate_presigned_url(file_key: str, expiration: int = 3600) -> str:
    """
    Generate a pre-signed URL for accessing an S3 file with detailed parameters.
    """
    try:
        print(f"Generating pre-signed URL for key: {file_key}")  # Debug log
        url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': AWS_S3_BUCKET,
                'Key': file_key,
                'ResponseContentDisposition': 'inline',  # Allows opening in the browser
            },
            ExpiresIn=expiration
        )
        print(f"Generated pre-signed URL: {url}")  # Debug log
        return url
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate pre-signed URL: {str(e)}")


def extract_file_key(s3_url: str) -> str:
    """
    Extract the S3 object key from the S3 URL.
    """
    prefix = f"https://{AWS_S3_BUCKET}.s3.amazonaws.com/"
    if not s3_url.startswith(prefix):
        raise ValueError("Invalid S3 URL format.")
    return s3_url[len(prefix):]
