from decouple import config
import boto3
import uuid
from datetime import datetime
from typing import Optional
from models.sheet_music import NoteCreate, NoteResponse

# AWS konfiguracija
AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY")
AWS_REGION = config("AWS_REGION")
BUCKET_NAME = config("BUCKET_NAME")
TABLE_NAME_NOTES = config("DYNAMODB_TABLE_NOTES")
TABLE_NAME_USERS = config("DYNAMODB_TABLE_USERS")

# AWS klijenti
s3_client = boto3.client('s3', 
    aws_access_key_id=AWS_ACCESS_KEY_ID, 
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY, 
    region_name=AWS_REGION)

dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)

# Funkcije

def upload_to_s3(user_id: str, file_data: bytes, file_extension: str = "pdf") -> str:
    """
    Upload datoteke u S3 bucket.
    """
    unique_id = str(uuid.uuid4())
    key = f"user_{user_id}/{unique_id}.{file_extension}"
    s3_client.put_object(Bucket=BUCKET_NAME, Key=key, Body=file_data)
    return f"https://{BUCKET_NAME}.s3.{AWS_REGION}.amazonaws.com/{key}"

def save_to_dynamodb(note_data: NoteCreate) -> NoteResponse:
    """
    Spremi metapodatke bilješke u DynamoDB.
    """
    table = dynamodb.Table(TABLE_NAME_NOTES)
    item = note_data.dict()
    item["id"] = str(uuid.uuid4())
    item["likes"] = 0
    item["datum_unosa"] = datetime.utcnow().isoformat()
    table.put_item(Item=item)
    return NoteResponse(**item)

def get_note_by_id(note_id: str) -> Optional[NoteResponse]:
    """
    Dohvati bilješku prema ID-u iz DynamoDB-a.
    """
    table = dynamodb.Table(TABLE_NAME_NOTES)
    response = table.get_item(Key={"id": note_id})
    if "Item" not in response:
        return None
    return NoteResponse(**response["Item"])

def update_note(note_id: str, updates: dict) -> Optional[NoteResponse]:
    """
    Ažuriraj bilješku u DynamoDB-u prema ID-u.
    """
    table = dynamodb.Table(TABLE_NAME_NOTES)
    update_expression = "SET " + ", ".join([f"{k} = :{k}" for k in updates.keys()])
    expression_values = {f":{k}": v for k, v in updates.items()}
    response = table.update_item(
        Key={"id": note_id},
        UpdateExpression=update_expression,
        ExpressionAttributeValues=expression_values,
        ReturnValues="ALL_NEW"
    )
    if "Attributes" not in response:
        return None
    return NoteResponse(**response["Attributes"])
