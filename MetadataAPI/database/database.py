import boto3
import uuid
from decouple import config
from typing import Optional, List

AWS_ACCESS_KEY_ID = config("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = config("AWS_SECRET_ACCESS_KEY")
AWS_REGION = config("AWS_REGION")
TABLE_NAME_METADATA = config("DYNAMODB_TABLE_METADATA")


dynamodb = boto3.resource("dynamodb", region_name=AWS_REGION)

def save_metadata(metadata_data: dict) -> dict:
    table = dynamodb.Table(TABLE_NAME_METADATA)
    metadata_data["score_id"] = metadata_data.get("score_id", str(uuid.uuid4()))
    table.put_item(Item=metadata_data)
    return metadata_data

def get_metadata(score_id: str) -> Optional[dict]:
    table = dynamodb.Table(TABLE_NAME_METADATA)
    response = table.get_item(Key={"score_id": score_id})
    return response.get("Item")

def update_metadata(score_id: str, updates: dict) -> Optional[dict]:
    table = dynamodb.Table(TABLE_NAME_METADATA)
    update_expression = "SET " + ", ".join([f"{k} = :{k}" for k in updates.keys()])
    expression_values = {f":{k}": v for k, v in updates.items()}
    response = table.update_item(
        Key={"score_id": score_id},
        UpdateExpression=update_expression,
        ExpressionAttributeValues=expression_values,
        ReturnValues="ALL_NEW"
    )
    return response.get("Attributes")

def delete_metadata(score_id: str) -> bool:
    table = dynamodb.Table(TABLE_NAME_METADATA)
    response = table.delete_item(
        Key={"score_id": score_id},
        ReturnValues="ALL_OLD"
    )
    return "Attributes" in response

def list_all_metadata() -> List[dict]:
    table = dynamodb.Table(TABLE_NAME_METADATA)
    response = table.scan()

    items = response.get("Items", [])
    print("Fetched metadata from database:", items)  # Debug

    # Osiguraj da svi zapisi imaju potrebna polja
    cleaned_items = [
        {
            "score_id": m.get("score_id", "unknown"),
            "title": m.get("title", "Untitled"),
            "composer": m.get("composer", "Unknown Composer"),
            "uploaded_at": m.get("uploaded_at", None)
        }
        for m in items
    ]

    return cleaned_items



