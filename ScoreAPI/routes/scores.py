from fastapi import APIRouter, UploadFile, HTTPException, Query
from typing import List
from database import upload_to_s3, delete_from_s3, list_files
from models import FileUploadResponse, FileListResponse

# FastAPI instanca
router = APIRouter()


@router.post("/upload", response_model=FileUploadResponse)
def upload_score(user_id: str = Query(...), file: UploadFile = None):
    """
    Upload notnog zapisa u S3.
    """
    if not file:
        raise HTTPException(status_code=400, detail="File is required")
    file_url = upload_to_s3(user_id, file)
    return FileUploadResponse(file_url=file_url)

@router.delete("/delete")
def delete_score(file_key: str = Query(...)):
    """
    Brisanje notnog zapisa iz S3.
    """
    try:
        delete_from_s3(file_key)
        return {"detail": "File deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete file: {str(e)}")

@router.get("/list", response_model=FileListResponse)
def list_scores(user_id: str = Query(...)):
    """
    Popis svih datoteka korisnika iz S3.
    """
    files = list_files(user_id)
    return FileListResponse(files=files)
