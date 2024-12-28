from fastapi import APIRouter, File, UploadFile, HTTPException
from app.database import upload_to_s3

router = APIRouter()

@router.post("/upload")
async def upload_note(user_id: int, file: UploadFile = File(...)):
    try:
        file_content = await file.read()
        url = upload_to_s3(user_id, file_content, file.filename.split(".")[-1])
        return {"message": "File uploaded successfully!", "url": url}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))