from fastapi import APIRouter, UploadFile, HTTPException, Depends, Form, File, Query
import httpx
import asyncio
from models.score import FileUploadResponse, FileListResponse, FileInfo, DeleteScoreRequest
from utils.utils import verify_user, create_or_update_metadata, delete_metadata
from database.database import upload_to_s3, delete_from_s3, list_files

router = APIRouter()

@router.post("/upload", response_model=FileUploadResponse)
async def upload_score(
    title: str = Form(...),
    composer: str = Form(...),
    file: UploadFile = File(...),
    current_user: str = Depends(verify_user)
):
    if not file:
        raise HTTPException(status_code=400, detail="File is required")
    
    file_url = upload_to_s3(current_user, file)
    score_id = file_url.split("/")[-1].split(".")[0]
    
    try:
        metadata_response = await create_or_update_metadata(score_id, current_user, title, composer)
    except HTTPException as e:
        delete_from_s3(file_url)
        raise HTTPException(status_code=e.status_code, detail=f"Metadata error: {e.detail}")
    
    return FileUploadResponse(file_url=file_url, metadata=metadata_response)

@router.delete("/delete")
async def delete_score(
    delete_request: DeleteScoreRequest,
    current_user: str = Depends(verify_user)
):

    if f"user_{current_user}/" not in delete_request.file_key:
        raise HTTPException(status_code=403, detail="You are not authorized to delete this file")
    
    try:
        delete_from_s3(delete_request.file_key)
        score_id = delete_request.file_key.split("/")[-1].split(".")[0]
        metadata_response = await delete_metadata(score_id)
        return metadata_response
    except HTTPException as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete score: {str(e)}")

@router.get("/list", response_model=FileListResponse)
async def list_scores(
    current_user: str = Depends(verify_user),
    query: str = Query(None)
):
    try:
        files = list_files(current_user)
        async with httpx.AsyncClient() as client:
            metadata_responses = await asyncio.gather(
                *[client.get(f"http://127.0.0.1:8002/metadata?score_id={file.split('/')[-1].split('.')[0]}")
                  for file in files]
            )
        metadata_list = [resp.json() if resp.status_code == 200 else None for resp in metadata_responses]
        file_info_list = [FileInfo(file_url=file, metadata=meta) for file, meta in zip(files, metadata_list)]
        
        if query:
            file_info_list = [info for info in file_info_list if info.metadata and query.lower() in info.metadata.get("title", "").lower()]
        
        return FileListResponse(files=file_info_list)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list files: {str(e)}")
