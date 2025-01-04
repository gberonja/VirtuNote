from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from app.database import upload_to_s3, save_to_dynamodb, dynamodb, TABLE_NAME_NOTES
from boto3.dynamodb.conditions import Attr
from app.auth import get_current_user

router = APIRouter()

# Upload notnog zapisa (zaštićeno)
@router.post("/upload")
async def upload_note(user_id: str, file: UploadFile = File(...), current_user: str = Depends(get_current_user)):
    """Endpoint za upload notnog zapisa na S3 i spremanje metapodataka u DynamoDB (zaštićeno)."""
    try:
        file_content = await file.read()
        url = upload_to_s3(user_id, file_content, file.filename.split(".")[-1])
        metadata = save_to_dynamodb(user_id, url)
        return {"message": "File uploaded successfully!", "url": url, "metadata": metadata}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Prikaz određenog notnog zapisa (zaštićeno)
@router.get("/{id}")
def get_note_by_id(id: str, current_user: str = Depends(get_current_user)):
    """Endpoint za dohvat zapisa prema ID-u (zaštićeno)."""
    try:
        table = dynamodb.Table(TABLE_NAME_NOTES)
        response = table.get_item(Key={"id": id})
        if "Item" not in response:
            raise HTTPException(status_code=404, detail="Note not found")
        return response["Item"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Prikaz svih notnih zapisa (ili filtriranih po korisniku, zaštićeno)
@router.get("/")
def get_all_notes(user_id: str = None, current_user: str = Depends(get_current_user)):
    """Endpoint za dohvat svih zapisa ili filtriranih po korisniku (zaštićeno)."""
    try:
        table = dynamodb.Table(TABLE_NAME_NOTES)
        if user_id:
            response = table.scan(FilterExpression=Attr("korisnik").eq(user_id))
        else:
            response = table.scan()
        return response["Items"]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Brisanje notnog zapisa prema ID-u (zaštićeno)
@router.delete("/{id}")
def delete_note_by_id(id: str, current_user: str = Depends(get_current_user)):
    """Endpoint za brisanje zapisa prema ID-u (zaštićeno)."""
    try:
        table = dynamodb.Table(TABLE_NAME_NOTES)
        response = table.delete_item(Key={"id": id})
        if response.get("ResponseMetadata", {}).get("HTTPStatusCode") != 200:
            raise HTTPException(status_code=500, detail="Failed to delete note")
        return {"message": "Note deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
