from decouple import config
import boto3
import uuid
from datetime import datetime
from typing import Optional

AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY")
AWS_REGION = config("AWS_REGION")
TABLE_NAME_USERS = config("DYNAMODB_TABLE_USERS")

# Initialize the DynamoDB resource
dynamodb = boto3.resource(
    "dynamodb",
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)

def save_user_to_dynamodb(user_data: dict) -> dict:
    table = dynamodb.Table(TABLE_NAME_USERS)
    user_data["id"] = str(uuid.uuid4())
    user_data["created_at"] = datetime.utcnow().isoformat()
    table.put_item(Item=user_data)
    return user_data

def get_user_by_id(user_id: str) -> Optional[dict]:
    table = dynamodb.Table(TABLE_NAME_USERS)
    response = table.get_item(Key={"id": user_id})
    return response.get("Item")

def get_user_by_username(username: str) -> Optional[dict]:
    table = dynamodb.Table(TABLE_NAME_USERS)
    response = table.scan(
        FilterExpression="username = :username",
        ExpressionAttributeValues={":username": username}
    )
    users = response.get("Items", [])
    return users[0] if users else None

def update_user(user_id: str, updates: dict) -> Optional[dict]:
    table = dynamodb.Table(TABLE_NAME_USERS)
    update_expression = "SET " + ", ".join([f"{k} = :{k}" for k in updates.keys()])
    expression_values = {f":{k}": v for k, v in updates.items()}
    response = table.update_item(
        Key={"id": user_id},
        UpdateExpression=update_expression,
        ExpressionAttributeValues=expression_values,
        ReturnValues="ALL_NEW"
    )
    return response.get("Attributes")

def delete_user(user_id: str) -> Optional[dict]:
    table = dynamodb.Table(TABLE_NAME_USERS)
    response = table.delete_item(
        Key={"id": user_id},
        ReturnValues="ALL_OLD"
    )
    return response.get("Attributes")

def get_all_users(limit: int = 100, last_key: Optional[dict] = None) -> dict:
    table = dynamodb.Table(TABLE_NAME_USERS)
    scan_kwargs = {"Limit": limit}
    if last_key:
        scan_kwargs["ExclusiveStartKey"] = last_key
    response = table.scan(**scan_kwargs)
    users = response.get("Items", [])
    return {
        "users": users,
        "last_evaluated_key": response.get("LastEvaluatedKey", None)
    }
