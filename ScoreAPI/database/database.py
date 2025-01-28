import boto3
import uuid
from decouple import config

# AWS konfiguracija
AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY")
AWS_REGION = config("AWS_REGION")
TABLE_NAME_NOTES = config("DYNAMODB_TABLE_NOTES")

# AWS klijent
s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

def upload_to_s3(user_id: str, file) -> str:
    """
    Upload datoteke u S3 bucket.
    """
    unique_id = str(uuid.uuid4())
    file_extension = file.filename.split(".")[-1]
    key = f"user_{user_id}/{unique_id}.{file_extension}"
    s3_client.upload_fileobj(file.file, TABLE_NAME_NOTES, key)
    return f"https://{TABLE_NAME_NOTES}.s3.{AWS_REGION}.amazonaws.com/{key}"

def delete_from_s3(file_key: str):
    """
    Brisanje datoteke iz S3 bucketa.
    """
    s3_client.delete_object(Bucket=TABLE_NAME_NOTES, Key=file_key)

def list_files(user_id: str) -> list:
    """
    Dohvaćanje popisa datoteka korisnika iz S3.
    """
    prefix = f"user_{user_id}/"
    response = s3_client.list_objects_v2(Bucket=TABLE_NAME_NOTES, Prefix=prefix)
    if "Contents" not in response:
        return []
    return [f"https://{TABLE_NAME_NOTES}.s3.{AWS_REGION}.amazonaws.com/{obj['Key']}" for obj in response["Contents"]]
