from fastapi import APIRouter, File, UploadFile, Query, HTTPException, Depends
from database.database import upload_to_s3, save_to_dynamodb, dynamodb, TABLE_NAME_NOTES
from boto3.dynamodb.conditions import Attr
from auth.auth import get_current_user
from models.sheet_music import NoteCreate, NoteResponse
from datetime import datetime
from typing import List, Optional, Literal
import logging
logging.basicConfig(level=logging.INFO)


router = APIRouter()

@router.post("/upload", response_model=NoteResponse)
async def upload_note(
    title: str = Query(..., min_length=1, max_length=100),
    description: str = Query("", max_length=500),
    tags: Literal["classical", "folk", "pop", "rock"] = Query("classical"),
    file: UploadFile = File(...),
    current_user: str = Depends(get_current_user),
):
    """Endpoint to upload sheet music to S3 and save metadata in DynamoDB (protected)."""
    try:
        # Check if the file is a PDF
        if not file.filename.lower().endswith(".pdf"):
            raise HTTPException(status_code=400, detail="Only PDF files are allowed.")
        
        # Read the file content
        file_content = await file.read()

        # Upload the file to S3
        url = upload_to_s3(current_user, file_content, file.filename.split(".")[-1])

        # Prepare metadata and validate with Pydantic
        note_metadata = NoteCreate(
            user_id=current_user,
            file_url=url,
            description=description,
            title=title,
            tags=tags,
            datum_unosa=datetime.utcnow().isoformat()
        )
        saved_note = save_to_dynamodb(note_metadata)

        # Return the created note
        return saved_note
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{id}")
def delete_note_by_id(
    id: str, 
    current_user: str = Depends(get_current_user)
):
    """Endpoint to delete a specific sheet music record by ID (protected). Only the owner can delete."""
    try:
        table = dynamodb.Table(TABLE_NAME_NOTES)
        response = table.get_item(Key={"id": id})
        if "Item" not in response:
            raise HTTPException(status_code=404, detail="Note not found")
        
        note = response["Item"]
        if note["user_id"] != current_user:
            raise HTTPException(status_code=403, detail="You can only delete your own notes.")
        
        table.delete_item(Key={"id": id})
        return {"message": "Note deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[NoteResponse])
def get_all_notes(
    title: Optional[str] = Query(None),
    tags: Optional[List[Literal["classical", "folk", "pop", "rock"]]] = Query(None),
    current_user: str = Depends(get_current_user)
):
    """Endpoint to fetch all sheet music or filter by title or tags."""
    try:
        table = dynamodb.Table(TABLE_NAME_NOTES)
        filter_expression = None
        
        # Filter by title if provided
        if title:
            filter_expression = Attr("title").contains(title)
        
        # Filter by tags if provided
        if tags:
            tag_filter = Attr("tags").is_in(tags)
            filter_expression = filter_expression & tag_filter if filter_expression else tag_filter
        
        # Fetch notes with applied filters
        if filter_expression:
            response = table.scan(FilterExpression=filter_expression)
        else:
            response = table.scan()

        # Ensure proper structure and map the data to NoteResponse
        notes = []
        for item in response["Items"]:
            try:
                # Ensuring all required fields are in place and converting them to NoteResponse
                note = NoteResponse(
                    id=item["id"],
                    user_id=item["user_id"],
                    title=item["title"],
                    description=item.get("description", ""),
                    tags=item.get("tags", "classical"),
                    file_url=item["file_url"],
                    datum_unosa=item["datum_unosa"],
                    komentari=item.get("komentari", []),
                    broj_likeova=item.get("likes", 0)
                )
                notes.append(note)
            except KeyError as e:
                raise HTTPException(status_code=500, detail=f"Missing field in database entry: {e}")
        
        return notes

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{id}/like", response_model=NoteResponse)
def like_note(
    id: str, 
    current_user: str = Depends(get_current_user)
):
    """Endpoint to like a specific sheet music record (protected)."""
    try:
        table = dynamodb.Table(TABLE_NAME_NOTES)
        
        # Pokušaj dobiti podatke o notama iz DynamoDB
        response = table.get_item(Key={"id": id})
        
        if "Item" not in response:
            raise HTTPException(status_code=404, detail="Note not found")
        
        note = response["Item"]
        
        # Provjera i inicijalizacija likes polja ako ne postoji
        if "likes" not in note:
            note["likes"] = 0  # Ako nema likes, postavite na 0
        
        # Povećanje broja lajkova
        note["likes"] += 1
        
        # Ažuriranje stavke u DynamoDB
        table.put_item(Item=note)

        # Vraćanje ažuriranih podataka u odgovoru
        return NoteResponse(
            id=note["id"],
            user_id=note["user_id"],
            title=note["title"],
            description=note.get("description", ""),
            tags=note.get("tags", "classical"),
            file_url=note["file_url"],
            datum_unosa=note["datum_unosa"],
            komentari=note.get("komentari", []),
            broj_likeova=note["likes"]  # Vraćanje ažuriranog broja lajkova
        )
    
    except Exception as e:
        # Dodajemo logiranje greške za bolju vidljivost
        print(f"Error while liking note: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while processing your request.")


@router.post("/{id}/comment", response_model=NoteResponse)
def add_comment_to_note(
    id: str, 
    comment: str, 
    current_user: str = Depends(get_current_user)
):
    """Endpoint to add a comment to a specific sheet music record (protected)."""
    try:
        table = dynamodb.Table(TABLE_NAME_NOTES)
        response = table.get_item(Key={"id": id})
        if "Item" not in response:
            raise HTTPException(status_code=404, detail="Note not found")
        
        note = response["Item"]
        note.setdefault("komentari", []).append({"user": current_user, "comment": comment})
        table.put_item(Item=note)
        return NoteResponse(**note)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



@router.get("/{id}/download")
def download_note(
    id: str, 
    current_user: str = Depends(get_current_user)
):
    """Endpoint to download the file of a specific sheet music record (protected)."""
    try:
        table = dynamodb.Table(TABLE_NAME_NOTES)
        response = table.get_item(Key={"id": id})
        if "Item" not in response:
            raise HTTPException(status_code=404, detail="Note not found")
        note = response["Item"]
        file_url = note.get("file_url")
        if not file_url:
            raise HTTPException(status_code=404, detail="File not found")
        return {"file_url": file_url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
