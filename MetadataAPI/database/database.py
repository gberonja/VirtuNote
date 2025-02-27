from decouple import config
import boto3
import uuid
from datetime import datetime
from typing import Optional, List

AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY")
AWS_REGION = config("AWS_REGION")
DYNAMODB_TABLE_METADATA = config("DYNAMODB_TABLE_METADATA")

dynamodb = boto3.resource(
    'dynamodb',
    region_name=AWS_REGION,
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY
)


def save_metadata(metadata_data: dict) -> dict:
    table = dynamodb.Table(DYNAMODB_TABLE_METADATA)

    metadata_data["id"] = metadata_data.get("id", str(uuid.uuid4()))
    metadata_data["broj_likeova"] = metadata_data.get(
        "broj_likeova", metadata_data.get("likes", 0))
    metadata_data["datum_unosa"] = metadata_data.get(
        "datum_unosa", datetime.utcnow().isoformat())
    metadata_data["komentari"] = metadata_data.get("komentari", [])
    metadata_data["likes_by_users"] = metadata_data.get("likes_by_users", [])

    table.put_item(Item=metadata_data)
    return metadata_data


def get_metadata(score_id: str) -> Optional[dict]:
    table = dynamodb.Table(DYNAMODB_TABLE_METADATA)
    response = table.get_item(Key={"id": score_id})
    return response.get("Item")


def update_metadata(score_id: str, updates: dict) -> Optional[dict]:
    table = dynamodb.Table(DYNAMODB_TABLE_METADATA)

    update_expression = "SET " + \
        ", ".join([f"{k} = :{k}" for k in updates.keys()])
    expression_values = {f":{k}": v for k, v in updates.items()}

    response = table.update_item(
        Key={"id": score_id},
        UpdateExpression=update_expression,
        ExpressionAttributeValues=expression_values,
        ReturnValues="ALL_NEW"
    )

    return response.get("Attributes")


def delete_metadata(score_id: str) -> bool:
    table = dynamodb.Table(DYNAMODB_TABLE_METADATA)
    response = table.delete_item(
        Key={"id": score_id},
        ReturnValues="ALL_OLD"
    )

    return "Attributes" in response


def add_comment(score_id: str, user_id: str, comment_text: str) -> Optional[dict]:
    metadata = get_metadata(score_id)
    if not metadata:
        return None

    new_comment = {
        "user_id": user_id,
        "content": comment_text,
        "timestamp": datetime.utcnow().isoformat()
    }

    comments = metadata.get("komentari", [])
    comments.append(new_comment)

    return update_metadata(score_id, {"komentari": comments})


def add_like(score_id: str, user_id: str) -> Optional[dict]:
    metadata = get_metadata(score_id)
    if not metadata:
        return None

    likes_by_users = metadata.get("likes_by_users", [])
    if user_id in likes_by_users:
        return metadata

    likes_by_users.append(user_id)

    current_likes = metadata.get("broj_likeova", metadata.get("likes", 0))

    return update_metadata(score_id, {
        "broj_likeova": current_likes + 1,
        "likes_by_users": likes_by_users
    })


def list_all_metadata(user_id: Optional[str] = None, tags: Optional[List[str]] = None,
                      title_contains: Optional[str] = None) -> List[dict]:
    table = dynamodb.Table(DYNAMODB_TABLE_METADATA)

    scan_kwargs = {}

    if user_id:
        filter_expression = boto3.dynamodb.conditions.Attr(
            "user_id").eq(user_id)
        scan_kwargs["FilterExpression"] = filter_expression

    response = table.scan(**scan_kwargs)
    items = response.get("Items", [])

    if tags:
        items = [item for item in items if item.get("tags") in tags]

    if title_contains:
        items = [item for item in items if title_contains.lower()
                 in item.get("title", "").lower()]

    return items
