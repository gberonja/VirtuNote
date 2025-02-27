import boto3
import uuid
from decouple import config
from io import BytesIO
from typing import Optional, BinaryIO

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


def upload_to_s3(user_id: str, file_content: BinaryIO, file_extension: str = "pdf") -> str:
    unique_id = str(uuid.uuid4())
    key = f"user_{user_id}/{unique_id}.{file_extension}"

    if isinstance(file_content, bytes):
        file_object = BytesIO(file_content)
    else:
        file_object = file_content

    s3_client.upload_fileobj(file_object, AWS_S3_BUCKET_NAME, key)
    return f"https://{AWS_S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{key}"


def delete_from_s3(file_key: str) -> bool:
    try:
        s3_client.delete_object(Bucket=AWS_S3_BUCKET_NAME, Key=file_key)
        return True
    except Exception as e:
        print(f"Error deleting file from S3: {e}")
        return False


def list_files(user_id: Optional[str] = None) -> list:
    prefix = f"user_{user_id}/" if user_id else ""
    response = s3_client.list_objects_v2(
        Bucket=AWS_S3_BUCKET_NAME, Prefix=prefix)
    if "Contents" not in response:
        return []
    return [
        f"https://{AWS_S3_BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{obj['Key']}"
        for obj in response["Contents"]
    ]


def get_s3_key_from_url(url: str) -> str:
    parts = url.split('/')
    return '/'.join(parts[3:])
