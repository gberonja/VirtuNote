from decouple import config
import boto3
import uuid

# Učitaj postavke iz .env datoteke
AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY")
AWS_REGION = config("AWS_REGION")
BUCKET_NAME = config("BUCKET_NAME")

# Postavi S3 klijent
s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

def upload_to_s3(user_id: int, file_data: bytes, file_extension: str = "pdf") -> str:
    unique_id = str(uuid.uuid4())
    key = f"user_{user_id}/{unique_id}.{file_extension}"
    s3_client.put_object(Bucket=BUCKET_NAME, Key=key, Body=file_data)
    return f"s3://{BUCKET_NAME}/{key}"
