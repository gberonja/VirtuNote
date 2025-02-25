import boto3
import uuid
from decouple import config

AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY")
AWS_REGION = config("AWS_REGION")
AWS_S3_BUCKET_NAME = config("AWS_S3_BUCKET_NAME")

s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

def upload_to_s3(user_id: str, file) -> str:
    unique_id = str(uuid.uuid4())
    file_extension = file.filename.split(".")[-1]
    key = f"user_{user_id}/{unique_id}.{file_extension}"
    s3_client.upload_fileobj(file.file, AWS_S3_BUCKET_NAME, key)
    return f"https://{AWS_S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{key}"

def delete_from_s3(file_key: str):
    """Deletes a file from the S3 bucket."""
    s3_client.delete_object(Bucket=AWS_S3_BUCKET_NAME, Key=file_key)

def list_files(user_id: str = None) -> list:
    prefix = f"user_{user_id}/" if user_id else ""
    response = s3_client.list_objects_v2(Bucket=AWS_S3_BUCKET_NAME, Prefix=prefix)
    if "Contents" not in response:
        return []
    return [f"https://{AWS_S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{obj['Key']}" for obj in response["Contents"]]
