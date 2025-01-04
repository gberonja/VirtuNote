from decouple import config
import boto3
import uuid
from datetime import datetime

# Postavke iz .env file-a
AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY")
AWS_REGION = config("AWS_REGION")
BUCKET_NAME = config("BUCKET_NAME")
TABLE_NAME_NOTES = config("DYNAMODB_TABLE_NOTES")
TABLE_NAME_USERS = config("DYNAMODB_TABLE_USERS")

# S3 klijent
s3_client = boto3.client(
    's3',
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

def upload_to_s3(user_id: str, file_data: bytes, file_extension: str = "pdf") -> str:
    """Uploada datoteku na S3 i vraća S3 URL."""
    unique_id = str(uuid.uuid4())
    key = f"user_{user_id}/{unique_id}.{file_extension}"
    s3_client.put_object(Bucket=BUCKET_NAME, Key=key, Body=file_data)
    return f"s3://{BUCKET_NAME}/{key}"

# DynamoDB klijent
dynamodb = boto3.resource(
    'dynamodb',
    region_name=AWS_REGION  # Dodaj regiju
)

def save_to_dynamodb(user_id: str, url: str):
    """Spremanje metapodataka u tablicu bilješki (notni_zapisi)."""
    table = dynamodb.Table(TABLE_NAME_NOTES)  # Koristi naziv tablice iz `.env`
    item = {
        "id": str(uuid.uuid4()),
        "korisnik": user_id,  # Spremi user_id kao string
        "datum_unosa": datetime.now().isoformat(),
        "url": url,
        "broj_likeova": 0,
        "komentari": []
    }
    table.put_item(Item=item)
    return item
