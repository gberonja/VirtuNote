from decouple import config
import boto3
import uuid
from datetime import datetime
from typing import Optional

# AWS konfiguracija
AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY")
AWS_REGION = config("AWS_REGION")
TABLE_NAME_USERS = config("DYNAMODB_TABLE_USERS")

# AWS klijenti
dynamodb = boto3.resource('dynamodb', region_name=AWS_REGION)

def save_user_to_dynamodb(user_data: dict) -> dict:
    """
    Spremi korisnika u DynamoDB.
    """
    table = dynamodb.Table(TABLE_NAME_USERS)
    user_data["id"] = str(uuid.uuid4())
    user_data["created_at"] = datetime.utcnow().isoformat()
    table.put_item(Item=user_data)
    return user_data

def get_user_by_id(user_id: str) -> Optional[dict]:
    """
    Dohvati korisnika prema ID-u iz DynamoDB-a.
    """
    table = dynamodb.Table(TABLE_NAME_USERS)
    response = table.get_item(Key={"id": user_id})
    if "Item" not in response:
        return None
    return response["Item"]

def update_user(user_id: str, updates: dict) -> Optional[dict]:
    """
    Ažuriraj korisnika u DynamoDB-u prema ID-u.
    """
    table = dynamodb.Table(TABLE_NAME_USERS)
    update_expression = "SET " + ", ".join([f"{k} = :{k}" for k in updates.keys()])
    expression_values = {f":{k}": v for k, v in updates.items()}
    response = table.update_item(
        Key={"id": user_id},
        UpdateExpression=update_expression,
        ExpressionAttributeValues=expression_values,
        ReturnValues="ALL_NEW"
    )
    if "Attributes" not in response:
        return None
    return response["Attributes"]

def delete_user(user_id: str) -> Optional[dict]:
    """
    Obriši korisnika iz DynamoDB-a prema ID-u.
    """
    table = dynamodb.Table(TABLE_NAME_USERS)
    response = table.delete_item(
        Key={"id": user_id},
        ReturnValues="ALL_OLD"
    )
    if "Attributes" not in response:
        return None
    return response["Attributes"]
